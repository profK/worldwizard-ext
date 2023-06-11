import omni.ext
import omni.ui as ui
from pxr import Sdf, Usd
import omni.usd
import omni.kit.app
import os, time
import threading
import carb.events
from omni.kit.viewport.utility import get_active_viewport
 

class DebugWindow(ui.Window):
    outlabel: ui.Label = None
    def __init__(self):
        # this is how we call super
        # class's constructor
        super().__init__("Debug Window",width=300, height=300)
        with self.frame:
            with ui.VStack():
                self.outlabel = ui.Label("",word_wrap=True)

    def WriteLine(self,text:str):
       self.outlabel.text = self.outlabel.text+text+"\n" 

global debug_window
debug_window = DebugWindow()

#Utility Functions



def get_ext_root_path():
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module("worldwizard")
    path = manager.get_extension_path(ext_id) 
    return path 

def AddLayerReference(file_path):
    global debug_window 
    debug_window.WriteLine("Add layer "+file_path)
    global stage
    stage = omni.usd.get_context().get_stage()
    root_path=get_ext_root_path()
    primname:str= os.path.splitext(os.path.basename(file_path))[0]
    primpath:str = "/"+primname+"Ref"
    prim: Usd.Prim = stage.GetPrimAtPath(primpath)
    # You can use standard python list.insert to add the subLayer to any position in the list
    if not prim.IsValid() :
        prim = stage.DefinePrim(primpath)
        references: Usd.References = prim.GetReferences()
        references.AddReference(
            assetPath=os.path.join(root_path,file_path)
        )
    
 
#stage events

   
def stage_event_handler(event:carb.events.IEvent):
    global debug_window
    #No switch statenment in p3.7 :frown: 
   
 
stage_event_sub = (
    omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
        stage_event_handler, name="WWStageEventSub")
)

def do_when_thread(pred:callable,act:callable,args:list, sleepsecs:float):
    while not pred():
        time.sleep(sleepsecs)
    act(*args)

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def do_when(pred:callable,act:callable,args:list,sleepsecs:float=1.0):
    threading.Thread(target=do_when_thread, args=(pred,act,args,sleepsecs)).start()

#camera change listener
def on_cam_change(value, change_type: carb.settings.ChangeEventType):
    #TODO move grid to fill view frustrum
    pass 

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class WorldwizardExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        global ext_root_path  
        global stage
        global debug_window
        global viewport
        global camera
        global camera_change_sub

        viewport = get_active_viewport()
        camera = viewport.get_active_camera()
        camera_change_sub = omni.kit.app.SettingChangeSubscription("/exts/your.ext.name/test/test/value",
                                                                    on_cam_change)
        
       
        debug_window.WriteLine("[worldwizard] worldwizard startup")
        ext_root_path=get_ext_root_path() 
        self._count = 0
        stat = omni.usd.get_context().get_stage_loading_status()
        #TODO check if already loaded
        do_when(lambda : not omni.usd.get_context().get_stage() is None,
             AddLayerReference,("WWWidgetsLayer.usd",))
 

        #LoadLayer('WWWidgetsLayer.usd');
        """ with self._window.frame:
            with ui.VStack():
                label = ui.Label("")


                def on_click():
                    self._count += 1
                    label.text = f"count: {self._count}"

                def on_reset():
                    self._count = 0
                    label.text = "empty"

                on_reset()

                with ui.HStack():
                    ui.Button("Add", clicked_fn=on_click)
                    ui.Button("Reset", clicked_fn=on_reset) """

    def on_shutdown(self):
        #global debug_window
        #debug_window.WriteLine("[worldwizard] worldwizard shutdown")
        print("shutdown") 
