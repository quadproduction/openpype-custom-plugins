db = connect( 'mongodb://localhost/openpype' );

all_project_anatomy = db.settings.find({ type: { $in: ['project_anatomy', 'project_anatomy_versioned'] } });

all_project_anatomy.forEach(function (project_anatomy) {

    project_anatomy['data']['roots'] = {
        work: {
          windows: 'C:\\PROJECTS\\',
          darwin: rootDir,
          linux: rootDir
        }
    };

    db.settings.updateOne(
        { _id: project_anatomy['_id'] },
        { $set: { "data": project_anatomy['data'] } },
    );
});
