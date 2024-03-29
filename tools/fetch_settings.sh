
RST='\033[0m'             # Text Reset

# Regular Colors
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White

# Bold
BBlack='\033[1;30m'       # Black
BRed='\033[1;31m'         # Red
BGreen='\033[1;32m'       # Green
BYellow='\033[1;33m'      # Yellow
BBlue='\033[1;34m'        # Blue
BPurple='\033[1;35m'      # Purple
BCyan='\033[1;36m'        # Cyan
BWhite='\033[1;37m'       # White

script_dir=$(dirname "$0")

dump_mongo_settings () {
    HOST=$1 && PORT=$2
    mongodump --host=$HOST --port=$PORT --db=openpype --collection=settings --archive --quiet | mongorestore --host="localhost" --port=27017 --archive --drop --quiet --stopOnError
}

dump_projects () {
    HOST=$1 && PORT=$2
    mongodump --host=$HOST --port=$PORT --db=avalon --archive --quiet | mongorestore --host="localhost" --port=27017 --archive --drop --quiet --stopOnError
}

disable_module () {
  # echo "Disable module ${1}"
  mongosh --file ${script_dir}/disable_module.js --quiet --eval "var moduleName='${1}'"
}

change_root_dir () {
  if [ ! -d "$1" ]; then
    mkdir -p "$1"
  fi

  mongosh --file ${script_dir}/change_root_dir.js --eval "var rootDir='${1}'" --quiet
}

start_mongo () {
  # make sur that /mnt/data/mongodb/db/ exists
  if [ ! -d "/mnt/data" ]; then
    echo -e "${BRed}!!!${RST} /mnt/data does not exist"
    return 1
  elif [ ! -d "/mnt/data/mongodb/db" ]; then
    mkdir -p "/mnt/data/mongodb/db"
  fi

  docker ps | grep openpype-mongo &> /dev/null
  if [ $? -eq 0 ]; then
    return 0
  fi

  docker ps -a | grep openpype-mongo &> /dev/null
  if [ $? -eq 0 ]; then
    docker start openpype-mongo
    return 0
  fi

  docker ps -a | grep 27017 &> /dev/null
  if [ $? -eq 0 ]; then
    echo -e "${BRed}Port 27017 is already used${RST}"
    return 1
  fi

  docker run -p 27017:27017 -v /mnt/data/mongodb/db/ --name openpype-mongo -d mongo

}

# Main
main () {

  echo -e "${BGreen}>>>${RST} Checking mongodump install ... \c"
  if command -v mongodump &> /dev/null; then
    echo -e "${BGreen} OK ${RST}"
  else
    echo -e "${BRed} NOT FOUND ${RST}"
    exit 1
  fi

  echo -e "${BGreen}>>>${RST} Checking mongorestore install ... \c"
  if command -v mongorestore &> /dev/null; then
    echo -e "${BGreen} OK ${RST}"
  else
    echo -e "${BRed} NOT FOUND ${RST}"
    exit 1
  fi

  echo -e "${BGreen}>>>${RST} Checking mongoresh install ... \c"
  if command -v mongosh &> /dev/null; then
    echo -e "${BGreen} OK ${RST}"
  else
    echo -e "${BRed} NOT FOUND ${RST}"
    exit 1
  fi

  echo -e "${BGreen}>>>${RST} Checking docker install ... \c"
  if [ -S "/var/run/docker.sock" ]; then
    if stat -c "%a" /var/run/docker.sock | grep -q 660; then
      if command -v docker &> /dev/null; then
        echo -e "${BGreen} OK ${RST}"
      else
        echo -e "${BRed} NOT FOUND ${RST}"
        exit 1
      fi
    else
      echo -e "${BRed} Change permission for /var/run/docker.sock => chmod 666 /var/run/docker.sock ${RST}"
      exit 1
    fi
  else
    echo -e "${BRed} NOT FOUND ${RST}"
    exit 1
  fi

  echo -e "${BGreen}>>>${RST} Start New mongoDB docker instance ... \c"
  if start_mongo ; then
    echo -e "${BGreen} OK ${RST}"
  else
    echo -e "${BRed} FAILED ${RST}"
    exit 1
  fi

  echo -e "${BGreen}>>>${RST} Which settings do you want to fetch?"
  echo "    1) wizz"
  echo "    2) fixstudio"
  read -p "    " choice

  if [[ $choice == "1" || $choice == "wizz" ]]; then
    COMPAGNY="wizz"
    HOST="openpype-mongo"
    PORT=27017
  elif [[ $choice == "2" || $choice == "fixstudio" ]]; then
    COMPAGNY="fixstudio"
    HOST="fixmongodb"
    PORT=27017
  else
    echo -e "${BRed}!!!${RST} Invalid choice"
    return 1
  fi

  echo -e "${BGreen}>>>${RST} Fetching Openpype settings from ${Yellow}${HOST}:${PORT}${RST}... \c"
  if dump_mongo_settings $HOST $PORT; then
      echo -e "${BGreen}OK${RST}"
  else
      echo -e "${BRed} FAILED ${RST}"
      return 1
  fi

  read -p "    Do you want to fetch projects ? (y/n) " choice
  if [[ $choice == "y" ]]; then
    echo -e "${BGreen}>>>${RST} Fetching Openpype projects from ${Yellow}${HOST}:${PORT}${RST}... \c"
    if dump_projects $HOST $PORT; then
        echo -e "${BGreen}OK${RST}"
    else
        echo -e "${BRed} FAILED ${RST}"
        return 1
    fi
  fi

  RootDir=${HOME}/openpype/$COMPAGNY/project
  echo -e "${BGreen}>>>${RST} Change Default RootDir to ${RootDir} ... \c"
  if change_root_dir $RootDir; then
    echo -e "${BGreen}>>>${RST} Change Default RootDir to ${RootDir} ... ${BGreen}OK${RST}"
  else
    echo -e "${BGreen}>>>${RST} Change Default RootDir to ${RootDir} ... ${BRed} FAILED ${RST}"
    return 1
  fi

  echo -e "${BGreen}>>>${RST} Disable Sync Server ... \c"
  if disable_module "sync_server"; then
    echo -e "${BGreen}>>>${RST} Disable Sync Server ... ${BGreen}OK${RST}"
  else
    echo -e "${BGreen}>>>${RST} Disable Sync Server ... ${BRed}FAILED${RST}"
    return 1
  fi

  echo -e "${BGreen}>>>${RST} Disable Ftrack ... \c"
  if disable_module "ftrack"; then
    echo -e "${BGreen}>>>${RST} Disable Ftrack ... ${BGreen}OK${RST}"
  else
    echo -e "${BGreen}>>>${RST} Disable Ftrack ... ${BRed}FAILED${RST}"
    return 1
  fi

  echo -e "${BGreen}>>>${RST} Disable kitsu ... \c"
  if disable_module "kitsu"; then
    echo -e "${BGreen}>>>${RST} Disable kitsu ... ${BGreen}OK${RST}"
  else
    echo -e "${BGreen}>>>${RST} Disable kitsu ... ${BRed}FAILED${RST}"
    return 1
  fi

#   read -p "    Do you want to fetch a project ? (y/n) " choice
#   if [[ $choice == "y" ]]; then
#     echo -e "${BGreen}>>>${RST} Fetch Project ... \c"
#     if mongosh --file ./tools/fetch_project.js; then
#       echo -e "${BGreen}>>>${RST} Fetch Project ... ${BGreen}OK${RST}"
#     else
#       echo -e "${BGreen}>>>${RST} Fetch Project ... ${BRed}FAILED${RST}"
#       return 1
#     fi
#   fi

  # demander si on veut creer un nouveau project test
  # read -p "    Do you want to create a new project ? (y/n) " choice

  echo -e "${BGreen}>>> Please set your Openpype URL to mongodb://localhost:27017 ${RST} "

}

return_code=0
main || return_code=$?
exit $return_code