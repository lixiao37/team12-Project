from pybuilder.core import use_plugin

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.unittest")

default_task = "publish"

