"""Example reference module."""

from interfaces.module_interface import IModule, ModuleManifest


class ExampleModule(IModule):
    def __init__(self):
        self._ctx = None
        self.started = False

    def manifest(self):
        return ModuleManifest(
            module_id="example_module",
            name="Example Module",
            version="1.0.0",
            description="Reference module",
            dependencies=[],
            api_version="1.0",
            enabled=True,
            capabilities=["demo"],
        )

    def on_load(self, context):
        self._ctx = context

    def on_start(self):
        self.started = True
        self._ctx.events.publish("example.started", {"msg": "hello"})

    def on_stop(self):
        self.started = False

    def on_unload(self):
        self._ctx = None
