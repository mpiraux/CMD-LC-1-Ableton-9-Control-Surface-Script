#Transport.py 
#This is a stripped-down script, which uses the Framework classes to assign MIDI notes to play, stop and record.
from __future__ import with_statement
import Live # This allows us (and the Framework methods) to use the Live API on occasion
 # We will be using time functions for time-stamping our log file outputs

""" All of the Framework files are listed below, but we are only using using some of them in this script (the rest are commented out) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller

from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
 # Class attaching to the mixer of a given track
 # Class representing a ClipSlot within Live
 # Base class for classes encompasing other components to form complex components
 # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
 # Base class for all classes encapsulating functions in Live
 # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
 # Class for switching between modes, handle several functions with few controls
 # Class representing control elements that can send values
 # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
 # Class representing a slider on the controller
 # Class representing a track's EQ, it attaches to the last EQ device in the track
 # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section

from ShiftableDeviceComponent import ShiftableDeviceComponent
from FlashingButtonElement import FlashingButtonElement # Custom code from Aumhaa/livid for creating flashing buttons
from LC1_Map import * # This contains your custom-tailored configuration/layout. This is really the only thing you should be editing.
from LC1_DEFS import * # This contains some abstractions for making code more readable/easy to modify

from DetailViewControllerComponent import DetailViewControllerComponent
from _Generic.Devices import *
from CMDEncoderElement import CMDEncoderElement
# Global Variables
CHANNEL = 7 # 0 is for prototype 8 is production model


class LC1(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        is_momentary = True
        self._timer = 0                 #used for flashing states, and is incremented by each call from self._update_display()
        self._touched = 0    
        self.flash_status = 1        
        
        with self.component_guard():
            self._setup_transport_control()

            if USE_MIXER_CONTROLS == True:
                self.mixer_control()
            if USE_SESSION_VIEW == True:
                self.session_control()        
            self.setup_device_control()
    
    
    def _setup_transport_control(self):
        is_momentary = True # We'll only be using momentary buttons here
        transport = TransportComponent() #Instantiate a Transport Component
        """set up the buttons"""
        transport.set_play_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 60)) #ButtonElement(is_momentary, msg_type, channel, identifier) Note that the MIDI_NOTE_TYPE constant is defined in the InputControlElement module
        transport.set_stop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 61))
        transport.set_record_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 62))
        #transport.set_overdub_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 68))
        #transport.set_nudge_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 75), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 73)) #(up_button, down_button)
    #    transport.set_tap_tempo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 63))
        #transport.set_metronome_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 80)) #For some reason, in Ver 7.x.x this method's name has no trailing "e" , and must be called as "set_metronom_button()"...
        #transport.set_loop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 82))
        #transport.set_punch_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 85), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 87)) #(in_button, out_button)
        #transport.set_seek_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 90), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 92)) # (ffwd_button, rwd_button)
        """set up the sliders"""
        #transport.set_tempo_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 26), SliderElement(MIDI_CC_TYPE, CHANNEL, 25)) #(control, fine_control)
        #transport.set_song_position_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 24))
   

    def mixer_control(self):
        is_momentary = True
        self.num_tracks = N_TRACKS
        if(USE_SENDS == True):
            self.mixer = MixerComponent(N_TRACKS, N_SENDS_PER_TRACK, USE_MIXER_EQ, USE_MIXER_FILTERS)
        else:
            self.mixer = MixerComponent(N_TRACKS,0, USE_MIXER_EQ, USE_MIXER_FILTERS)
        self.mixer.name = 'Mixer'
        self.mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        for index in range(N_TRACKS):
            self.mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
            self.mixer.channel_strip(index)._invert_mute_feedback = True             


        if(USE_SELECT_BUTTONS == True):
            self.selectbuttons = [None for index in range(N_TRACKS)]
            for index in range(len(SELECT_BUTTONS)):
                self.selectbuttons[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,SELECT_BUTTONS[index], 'Select_Button', self)
                self.mixer.channel_strip(index).set_select_button(self.selectbuttons[index])
                self.selectbuttons[index].set_on_value(SELECT_BUTTON_ON_COLOR)
                self.selectbuttons[index].set_off_value(SELECT_BUTTON_OFF_COLOR)

        if(USE_SOLO_BUTTONS == True):
            self.solobuttons = [None for index in range(N_TRACKS)]
            for index in range(len(SOLO_BUTTONS)):
                self.solobuttons[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,SOLO_BUTTONS[index], 'Solo_Button', self)
                self.mixer.channel_strip(index).set_solo_button(self.solobuttons[index])
                self.solobuttons[index].set_on_value(SOLO_BUTTON_ON_COLOR)
                self.solobuttons[index].set_off_value(SOLO_BUTTON_OFF_COLOR)



        if(USE_ARM_BUTTONS == True):
            self.armbuttons = [None for index in range(N_TRACKS)]
            for index in range(len(ARM_BUTTONS)):
                self.armbuttons[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,ARM_BUTTONS[index], 'Arm_Button', self)
                self.mixer.channel_strip(index).set_arm_button(self.armbuttons[index])
                self.armbuttons[index].set_on_value(ARM_BUTTON_ON_COLOR)
                self.armbuttons[index].set_off_value(ARM_BUTTON_OFF_COLOR)
		
        if(USE_MUTE_BUTTONS == True):
            self.mutebuttons = [None for index in range(N_TRACKS)]
            for index in range(len(MUTE_BUTTONS)):
                self.mutebuttons[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,MUTE_BUTTONS[index], 'Mute_Button', self)
                self.mixer.channel_strip(index).set_mute_button(self.mutebuttons[index])
                self.mutebuttons[index].set_on_value(MUTE_BUTTON_ON_COLOR)
                self.mutebuttons[index].set_off_value(MUTE_BUTTON_OFF_COLOR)
                
        if(USE_SENDS == True):
            self.sendencoders = [None for index in range(len(SEND_ENCODERS))]
            for index in range(len(SEND_ENCODERS)):
                self.sendencoders[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL, SEND_ENCODERS[index], Live.MidiMap.MapMode.absolute)
            for index in range(len(SEND_ENCODERS)/N_SENDS_PER_TRACK):
                self.mixer.channel_strip(index).set_send_controls(tuple(self.sendencoders[(index*N_SENDS_PER_TRACK):((index*N_SENDS_PER_TRACK)+N_SENDS_PER_TRACK-1)]))

                
        if(USE_VOLUME_CONTROLS == True):
            self.volencoders = [None for index in range(len(VOLUME_ENCODERS))]
            for index in range (len(VOLUME_ENCODERS)):
                self.volencoders[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL, VOLUME_ENCODERS[index], Live.MidiMap.MapMode.absolute)
                self.mixer.channel_strip(index).set_volume_control(self.volencoders[index])
      
    def session_control(self):
        is_momentary = True
        self._timer = 0
        self.flash_status = 1
        self.grid = [None for index in range(N_TRACKS*N_SCENES)]
        for index in range(N_TRACKS*N_SCENES):
            self.grid[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,TRACK_CLIP_BUTTONS[index], 'Grid' + str(index), self)
            self.grid[index].set_off_value(127)
            self.grid[index].turn_off()
            
        self.matrix = ButtonMatrixElement()
        for row in range(N_SCENES):
            button_row = []
            for column in range(N_TRACKS):
                button_row.append(self.grid[row+(column*5)])
            self.matrix.add_row(tuple(button_row))
        self.session = SessionComponent(N_TRACKS,N_SCENES)
        self.session.name = "Session"
        self.session.set_offsets(0,0)

        self.scene = [None for index in range(N_SCENES)]
        for row in range(N_SCENES):
            self.scene[row] = self.session.scene(row)
            self.scene[row].name = 'Scene_'+str(row)
            for column in range(N_TRACKS):
                clip_slot = self.scene[row].clip_slot(column)
                clip_slot.name = str(column)+'_Clip_Slot'+str(row)
                self.scene[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRG_PLAY_COLOR)
                self.scene[row].clip_slot(column).set_stopped_value(CLIP_STOP_COLOR)
                self.scene[row].clip_slot(column).set_started_value(CLIP_STARTED_COLOR)
        self.set_highlighting_session_component(self.session)        
        self.session_zoom = DeprecatedSessionZoomingComponent(self.session)                 #this creates the ZoomingComponent that allows navigation when the shift button is pressed
        self.session_zoom.name = 'Session_Overview'                            #name it so we can access it in m4l
        self.session_zoom.set_stopped_value(ZOOM_STOPPED)            #set the zooms stopped color
        self.session_zoom.set_playing_value(ZOOM_PLAYING)            #set the zooms playing color
        self.session_zoom.set_selected_value(ZOOM_SELECTED)            #set the zooms selected color
        self.session_zoom.set_button_matrix(self.matrix)                        #assign the ButtonMatrixElement that we created in _setup_controls() to the zooming component so that we can control it
        self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 63)
        self.session_zoom.set_zoom_button(self._shift_button)                   #assign a shift button so that we can switch states between the SessionComponent and the SessionZoomingComponent

        self.log_message(str(len(STOP_BUTTONS)))
        if(USE_STOP_BUTTONS == True):
            self.stopbuttons = [None for index in range(N_TRACKS)]
            for index in range(len(STOP_BUTTONS)):
                self.stopbuttons[index] = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,STOP_BUTTONS[index], 'Stop_Button', self)
                self.session.set_stop_track_clip_buttons(self.stopbuttons)
                self.stopbuttons[index].set_on_value(STOP_BUTTON_ON_COLOR)
                self.stopbuttons[index].set_off_value(STOP_BUTTON_OFF_COLOR)
 

    # Clip trigger on grid assignments
        for column in range(N_TRACKS):
            for row in range(N_SCENES):
                self.scene[row].clip_slot(column).set_launch_button(self.grid[row+(column*5)])    
    
        for index in range(N_TRACKS*N_SCENES):
            self.grid[index].clear_send_cache()      
                
        if USE_SESSION_NAV == True:
            self.navleft = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,NAVBOX_LEFT_BUTTON, 'Nav_Left_Button', self)
            self.navleft.clear_send_cache()
            self.navleft.set_on_off_values(NAVBOX_LEFT_BUTTON_C, NAVBOX_LEFT_BUTTON_C)
            
            self.navright = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,NAVBOX_RIGHT_BUTTON, 'Nav_Right_Button', self)
            self.navright.clear_send_cache()
            self.navright.set_on_off_values(NAVBOX_RIGHT_BUTTON_C, NAVBOX_RIGHT_BUTTON_C)
            
            self.navup = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,NAVBOX_UP_BUTTON, 'Nav_Up_Button', self)
            self.navup.clear_send_cache()
            self.navup.set_on_off_values(NAVBOX_UP_BUTTON_C, NAVBOX_UP_BUTTON_C)
                 
            self.navdown = FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL,NAVBOX_DOWN_BUTTON, 'Nav_Down_Button', self)
            self.navdown.clear_send_cache()
            self.navdown.set_on_off_values(NAVBOX_DOWN_BUTTON_C, NAVBOX_DOWN_BUTTON_C) 
            
            self.session.set_track_bank_buttons(self.navright, self.navleft)
            self.session.set_scene_bank_buttons(self.navdown, self.navup)
        
        if USE_MIXER_CONTROLS == True:
            self.session.set_mixer(self.mixer)    

        self.refresh_state()
        self.session.set_enabled(True)
        self.session.update()  
              
    def setup_device_control(self):
        is_momentary = True
        device_bank_buttons = []
        device_param_controls = []
        bank_button_labels = ('Clip_Track_Button', 'Device_On_Off_Button', 'Previous_Device_Button', 'Next_Device_Button')
        for index in range(4):
            device_bank_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 16 + index))
            device_bank_buttons[-1].name = bank_button_labels[index]
        for index in range(8):
            #ring_mode_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, CHANNEL, 21 + index)
            ringed_encoder = CMDEncoderElement(MIDI_CC_TYPE, CHANNEL, 16 + index, Live.MidiMap.MapMode.relative_binary_offset, 20)
            #ringed_encoder.set_ring_mode_button(ring_mode_button)
            ringed_encoder.name = 'Device_Control_' + str(index)
            #ring_mode_button.name = ringed_encoder.name + '_Ring_Mode_Button'
            device_param_controls.append(ringed_encoder)

        device = ShiftableDeviceComponent()
        device.name = 'Device_Component'
        device.set_bank_buttons(tuple(device_bank_buttons))
        device.set_shift_button(self._shift_button)
        device.set_parameter_controls(tuple(device_param_controls))
        device.set_on_off_button(device_bank_buttons[1])
        self.set_device_component(device)
        detail_view_toggler = DetailViewControllerComponent(self)
        detail_view_toggler.name = 'Detail_View_Control'
        detail_view_toggler.set_shift_button(self._shift_button)
        detail_view_toggler.set_device_clip_toggle_button(device_bank_buttons[0])
        detail_view_toggler.set_device_nav_buttons(device_bank_buttons[2], device_bank_buttons[3])
        
    def update_display(self):
        ControlSurface.update_display(self)
        self._timer = (self._timer + 1) % 256
        self.flash()
        
    def flash(self):
        if(USE_SESSION_VIEW == True):
            for index in range(N_TRACKS*N_SCENES):
                if(self.grid[index]._flash_state > 0):
                    self.grid[index].flash(self._timer)    
        if(USE_SESSION_NAV == True):
            if(self.navleft._flash_state>0):
                    self.navleft.flash(self._timer)
            if(self.navright._flash_state>0):
                    self.navright.flash(self._timer)
            if(self.navup._flash_state>0):
                    self.navup.flash(self._timer)
            if(self.navdown._flash_state>0):
                    self.navdown.flash(self._timer)    
        if(USE_MIXER_CONTROLS == True):
            for index in range(N_TRACKS):
                if(USE_SOLO_BUTTONS == True):
                    if(self.solobuttons[index]._flash_state > 0):
                        self.solobuttons[index].flash(self._timer)                
                if(USE_MUTE_BUTTONS == True):
                    if(self.mutebuttons[index]._flash_state > 0):
                        self.mutebuttons[index].flash(self._timer)
                


    def disconnect(self):
        self._hosts = []
        ControlSurface.disconnect(self)
        return None        
