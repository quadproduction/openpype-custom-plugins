# Quad-Plugins Repository

Welcome to the **Quad-Plugins** repository! This repository contains a collection of plugins and modules designed for use with OpenPype, an open-source pipeline management tool. These plugins are developed to streamline various actions in the pipeline, such as creating, loading, and publishing steps. The repository also includes a module named **quad_pyblish_module**, which is intended for managing various plugins specifically tailored for OpenPype.

## Installation

To use the plugins from this repository. Follow the steps below to install and integrate these plugins into your OpenPype environment:

1. Clone the repository to your local machine using the following command:

  ```git clone https://github.com/quadproduction/quad-plugins```

2. Locate the OpenPypeAddOn Paths of your OpenPype installation : 

  ```OpenPype Settings > System > Modules > OpenPypeAddOn Paths ``` 


3. Copy the **quad-plugins** repository directory to the AddOn Path of OpenPype.


4. Now, you should have successfully installed the **quad-plugins** repository and its modules into your OpenPype environment.

## quad_pyblish_module

The main module included in this repository is **quad_pyblish_module**. However, please note that the name of this module is subject to change in the future, as it now contains various plugins that are specifically designed for OpenPype. Currently, the module is responsible for managing the following plugins:

- **Actions Plugin:** This plugin provides additional actions within OpenPype, allowing you to perform custom actions during different stages of the pipeline.
To use a custom Action plugin, you need to call the module that contains the plugin's class and inherit from the `Action` class. For example, if you have a custom `MyCustomAction` plugin, you can initialize it like this:

  ```python
  from pyblish.plugin import Action

  class MyCustomAction(Action):
    label = None # Optional label to display in place of class name.
    active = True # Whether or not to allow execution of action.
    icon = None # icon: Name, relative path or absolute path to image for use as an icon of this action. For relative paths, the current working directory of the host is used and names represent icons available via Awesome Icons. fortawesome.github.io/Font-Awesome/icons/
    on = "all" # When to enable this action; available options are:
    # - "all": Always available (default).
    # - "notProcessed": The plug-in has not yet been processed
    # - "processed": The plug-in has been processed
    # - "succeeded": The plug-in has been processed, and succeeded
    # - "failed": The plug-in has been processed, and failed
    # - "warning": The plug-in has been processed, and had a warning
    # - "failedOrWarning": The plug-in has been processed, and failed or had a warning
    pass
  ```
- **Create Plugin:** The Create plugin facilitates the creation of new assets within the pipeline. It streamlines the process of initializing new projects or assets.  
To use a custom Create plugin, you need to call the module that contains the plugin's class and inherit from the `Creator` class. For example, if you have a custom `MyCustomCreator` plugin, you can initialize it like this:
    ```python
    from openpype.pipeline.create import Creator
    
    class MyCustomCreator(Creator):
        label = None # Label shown in UI
        group_label = None # Group Label shown in UI
        order = 100 # Order in which will be plugin executed (collect & update instances) less == earlier -> Order '90' will be processed before '100'
        enabled = True # Creator is enabled 
        icon = None # Creator (and family) icon may not be used if `get_icon` is reimplemented
        instance_attr_defs = [] # Instance attribute definitions that can be changed per instance returns list of attribute definitions from `openpype.pipeline.attribute_definitions`
        host_name = None # Filtering by host name - can be used to be filtered by host name used on all hosts when set to 'None' for Backwards compatibility was added afterward
        pass
    ```

- **Load Plugin:** The Load plugin enables quick and efficient loading of assets into various applications used in the pipeline.
To use a custom Loader plugin, you need to call the module that contains the plugin's class and inherit from the `LoaderPlugin` class. For example, if you have a custom `MyCustomLoader` plugin, you can initialize it like this:

  ```python
  from openpype.pipeline.load import LoaderPlugin
  import qargparse
  
  class MyCustomLoader(LoaderPlugin):
    hosts = ["*"] # Optionally limit a plug-in to one or more hosts
    families = ["*"] # Optionally limit a plug-in to one or more families
    representations = [] # Optionally limit a plug-in to one or more representations
    extensions = {"*"} 
    order = -1 # Order in which this plug-in is processed
    is_multiple_contexts_compatible = False # Whether or not plug-in can be used with multiple contexts
    enabled = True # Whether or not to use plug-in during processing
    options = [qargparse.Integer(
            "count",
            label="Count",
            default=1,
            min=1,
            help="How many times to load?"
        )] # Options associated to this plug-in
    pass
  ```
- **Publish Plugin:** The Publish plugin automates the publishing process of assets, ensuring they are ready for the next stages of the pipeline or final delivery.
To use a custom Pyblish plugin, you need to call the module that contains the plugin's class and inherit from the `InstancePlugin` class. For example, if you have a custom `MyCustomPyblish` plugin, you can initialize it like this:
    ```python
    from pyblish.api import InstancePlugin
  
    class MyCustomPyblish(InstancePlugin):
        hosts = ["*"] # Optionally limit a plug-in to one or more hosts
        families = ["*"] # Optionally limit a plug-in to one or more families
        label = None # Printed name of plug-in
        active = True # Whether or not to use plug-in during processing
        version = (0, 0, 0) # Optional version for forwards-compatibility. (Pyblish Compatibility)
        order = -1 # Order in which this plug-in is processed
        optional = False # Whether or not plug-in can be skipped by the user.
        actions = [] # Actions associated to this plug-in
        # Other Attributes are available, please refer to the Pyblish documentation for more information.
        pass
    ```
## Issues

If you encounter any issues, bugs, or have feature requests related to the **quad-plugins** repository or any specific plugin within it, please don't hesitate to open a new issue on this repository. We will do our best to address and resolve the problem as soon as possible.
