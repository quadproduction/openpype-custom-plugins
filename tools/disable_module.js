db = connect('mongodb://localhost/openpype');

system_settings = db.settings.findOne({ type: 'system_settings' });

if (system_settings['data']['modules'].hasOwnProperty(moduleName)) {
    system_settings['data']['modules'][moduleName]['enabled'] = false;
}

db.settings.updateOne(
    { _id: system_settings['_id'] },
    { $set: { "data": system_settings['data'] } },
);