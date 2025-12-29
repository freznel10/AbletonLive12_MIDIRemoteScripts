# User.py For Ableton Live 11
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.DeviceComponent import DeviceComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.SliderElement import SliderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SessionComponent import SessionComponent
from _Framework.EncoderElement import *

from Launchpad.ConfigurableButtonElement import ConfigurableButtonElement


class user(ControlSurface):
  def __init__(self, c_instance):
    super(user, self).__init__(c_instance)
    self._parent = c_instance
   # self._css = c_instance
    with self.component_guard():
      self.log_message("csslog: it works!2")
    self._last_selected_param_values = None
    self._last_selected_param_device = None
    self._params_changed_latched = False
    self.target_devices_for_chains = [None] * 8
    self._setup_chains_listeners()
    self._inputs()
    self._selected_device_listener_track = None
    self._selected_device_for_chain_listener = None
    self._setup_selected_device_chain_listener()
      
    return
  
  # def get_banker_value(self, mod_name, param_index):
  #   base = mod_name
  #   computed = base + param_index
  #   return computed
  
  def get_banker_value(self, mod_name, param_index):
    base = mod_name
    computed = base + param_index
    return self.song().view.selected_track.view.selected_device.parameters[computed]

  def track_num(self, track_num):
    parent = getattr(self, "_parent", None)
    if parent is not None and hasattr(parent, "track_num"):
      try:
        return parent.track_num(track_num)
      except Exception:
        pass
    if hasattr(self, "_session") and self._session is not None:
      return track_num + self._session._track_offset
    return track_num

  def _get_selected_parameter_banked_value(self, mod_name, param_index):
    base = mod_name
    computed = base + param_index
    return self.song().view.selected_track.view.selected_device.parameters[computed]

  def get_selected_parameter_banked_value_1(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 1)

  def get_selected_parameter_banked_value_2(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 2)

  def get_selected_parameter_banked_value_3(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 3)

  def get_selected_parameter_banked_value_4(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 4)

  def get_selected_parameter_banked_value_5(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 5)

  def get_selected_parameter_banked_value_6(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 6)

  def get_selected_parameter_banked_value_7(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 7)

  def get_selected_parameter_banked_value_8(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 8)

  def get_selected_parameter_banked_value_9(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 9)

  def get_selected_parameter_banked_value_10(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 10)

  def get_selected_parameter_banked_value_11(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 11)

  def get_selected_parameter_banked_value_12(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 12)

  def get_selected_parameter_banked_value_13(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 13)

  def get_selected_parameter_banked_value_14(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 14)

  def get_selected_parameter_banked_value_15(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 15)

  def get_selected_parameter_banked_value_16(self, mod_name):
    return self._get_selected_parameter_banked_value(mod_name, 16)
  
  def disconnect(self):
    """
    Called when the script is disabled or reloaded.
    Clean up all listeners here.
    """
    self._remove_chains_listeners()
    self._remove_selected_device_chain_listener()
    super(user, self).disconnect()

  def update_display(self):
    super(user, self).update_display()
    if self.selected_device_params_changed():
      if not self._params_changed_latched:
        self._params_changed_latched = True
        self.log_message("csslog: Params Changed")
    else:
      self._params_changed_latched = False
    self._sync_selected_device_collapsed_controls()

  def _sync_selected_device_collapsed_controls(self, is_collapsed=None, element_names=None):
    """
    Keep specified controls in sync with the selected device collapse state.
    """
    parent = getattr(self, "_parent", None) or self
    if is_collapsed is None:
      try:
        song = self.song()
        view = song.view if song is not None else None
        sel_track = view.selected_track if view is not None else None
        sel_device = sel_track.view.selected_device if (sel_track is not None and hasattr(sel_track, "view")) else None
        if sel_device is None or not hasattr(sel_device, "view"):
          return
        is_collapsed = sel_device.view.is_collapsed
      except Exception as e:
        self.log_message(f"csslog: Error reading selected device collapse state: {e}")
        return

    desired = 0 if bool(is_collapsed) else 127

    if element_names is None:
      element_names = ["midi_cc_ch_15_val_122"]

    for name in element_names:
      ctrl = getattr(parent, name, None)
      if ctrl is None:
        continue
      cur_val = getattr(ctrl, "cur_val", None)
      if cur_val != desired:
        ctrl.send_value(int(desired))
        try:
          ctrl.cur_val = int(desired)
        except Exception:
          pass

  def _setup_chains_listeners(self):
    """
    Finds the target devices on tracks 0-7 and adds listeners to their chains.
    """
    for i in range(8):
        try:
            device = self.song().tracks[i].devices[0]
            if hasattr(device, 'chains'):
                self.target_devices_for_chains[i] = device
                device.add_chains_listener(self._on_chains_changed)
                self.log_message(f"csslog: Successfully added listener to device on track {i}.")
            else:
                self.log_message(f"csslog: Device on track {i} has no chains.")
        except IndexError:
            self.log_message(f"csslog: Could not find a device on track {i} to listen to.")
        except Exception as e:
            self.log_message(f"csslog: Error setting up chains listener for track {i}: {e}")
    self._log_all_chains() # Log initial state

  def _remove_chains_listeners(self):
    """
    Removes the chains listeners from the target devices if they exist.
    """
    for i, device in enumerate(self.target_devices_for_chains):
        try:
            if device and device.chains_has_listener(self._on_chains_changed):
                device.remove_chains_listener(self._on_chains_changed)
                self.log_message(f"csslog: Successfully removed chains listener from device on track {i}.")
        except Exception as e:
            self.log_message(f"csslog: Error removing chains listener for track {i}: {e}")

  def _on_chains_changed(self):
    """
    This function is called automatically when the chains of a listened-to device change.
    """
    self.log_message("csslog: Device chains changed, re-logging names...")
    self._log_all_chains()
    
  def _log_all_chains(self):
    """
    Logs the chains for all targeted devices.
    """
    for i, device in enumerate(self.target_devices_for_chains):
        self._log_device_chains(device, i + 1)

  def _log_device_chains(self, device, sysex_id):
    """
    Loops through the first 20 chain slots of the given device. It logs each
    chain's name and sends it to TouchOSC with the specified sysex_id.
    If a chain slot is empty, it sends '-----------' as a placeholder.
    """
    if device and hasattr(device, 'chains'):
        try:
            num_existing_chains = len(device.chains)

            for chain_number in range(20):
                chain_name = ""
                if chain_number < num_existing_chains:
                    chain_name = device.chains[chain_number].name or ""
                else:
                    chain_name = "-----------"

                """self.log_message(f"csslog: Sending chain {chain_number} for sysex_id {sysex_id}: {chain_name}")"""

                name_bytes = self._ascii7_bytes(chain_name)
                sysex_message = [240, 125, sysex_id, chain_number] + name_bytes + [247]
                self._send_midi(tuple(sysex_message))

        except Exception as e:
            self.log_message(f"csslog: An error occurred while processing device chains for sysex_id {sysex_id}: {e}")
    else:
        self.log_message(f"csslog: Target device for chain logging (sysex_id {sysex_id}) is not set or has no chains.")

  def _setup_selected_device_chain_listener(self):
    """
    Adds listeners for the selected track/device, and monitors chains on that device.
    """
    try:
      view = self.song().view
      if not view.selected_track_has_listener(self._on_selected_track_changed):
        view.add_selected_track_listener(self._on_selected_track_changed)
    except Exception as e:
      self.log_message(f"csslog: Error adding selected track listener: {e}")
    self._attach_selected_device_listener()
    self._on_selected_device_changed()

  def _remove_selected_device_chain_listener(self):
    """
    Removes listeners for the selected device/track chain monitoring.
    """
    try:
      view = self.song().view
      if view.selected_track_has_listener(self._on_selected_track_changed):
        view.remove_selected_track_listener(self._on_selected_track_changed)
    except Exception:
      pass
    self._detach_selected_device_listener()
    self._remove_selected_device_chains_listener()

  def _attach_selected_device_listener(self):
    track = None
    try:
      track = self.song().view.selected_track
    except Exception:
      track = None
    if track is None or not hasattr(track, "view"):
      return
    self._selected_device_listener_track = track
    try:
      if not track.view.selected_device_has_listener(self._on_selected_device_changed):
        track.view.add_selected_device_listener(self._on_selected_device_changed)
    except Exception:
      pass

  def _detach_selected_device_listener(self):
    track = getattr(self, "_selected_device_listener_track", None)
    if track is None or not hasattr(track, "view"):
      self._selected_device_listener_track = None
      return
    try:
      if track.view.selected_device_has_listener(self._on_selected_device_changed):
        track.view.remove_selected_device_listener(self._on_selected_device_changed)
    except Exception:
      pass
    self._selected_device_listener_track = None

  def _on_selected_track_changed(self):
    self._detach_selected_device_listener()
    self._attach_selected_device_listener()
    self._on_selected_device_changed()

  def _on_selected_device_changed(self):
    device = None
    try:
      track = self.song().view.selected_track
      if track is not None and hasattr(track, "view"):
        device = track.view.selected_device
    except Exception:
      device = None

    if device is self._selected_device_for_chain_listener:
      self._log_selected_device_chains(device)
      return

    self._remove_selected_device_chains_listener()
    if device is None or not hasattr(device, "chains"):
      self._selected_device_for_chain_listener = None
      return

    self._selected_device_for_chain_listener = device
    try:
      if not device.chains_has_listener(self._on_selected_device_chains_changed):
        device.add_chains_listener(self._on_selected_device_chains_changed)
    except Exception:
      pass
    self._log_selected_device_chains(device)

  def _remove_selected_device_chains_listener(self):
    device = getattr(self, "_selected_device_for_chain_listener", None)
    if device is None:
      return
    try:
      if device.chains_has_listener(self._on_selected_device_chains_changed):
        device.remove_chains_listener(self._on_selected_device_chains_changed)
    except Exception:
      pass
    self._selected_device_for_chain_listener = None

  def _on_selected_device_chains_changed(self):
    device = getattr(self, "_selected_device_for_chain_listener", None)
    if device is None:
      return
    self._log_selected_device_chains(device)

  def _log_selected_device_chains(self, device):
    if device is None or not hasattr(device, "chains"):
      return
    try:
      chains = list(device.chains) if device.chains is not None else []
    except Exception:
      chains = []
    if not chains:
      device_name = getattr(device, "name", "") or ""
      name_bytes = self._ascii7_bytes(device_name)
      sysex_message = [240, 124, 1, 0] + name_bytes + [247]
      self._send_midi(tuple(sysex_message))
      return
    device_address = self._absolute_device_path(device)
    self.log_message(f"csslog: Selected device address: {device_address}")
    for chain_number, chain in enumerate(chains):
      chain_name = getattr(chain, "name", "") or ""
      self.log_message(f"csslog: Selected device chain {chain_number}: {chain_name}")
      chain_address = f"{device_address}.chains[{chain_number}]"
      self.log_message(f"csslog: Selected device chain {chain_number} address: {chain_address}")
      name_bytes = self._ascii7_bytes(chain_name)
      sysex_message = [240, 124, 1, chain_number] + name_bytes + [247]
      self._send_midi(tuple(sysex_message))

  def _absolute_selected_track_path(self):
    song = self.song()
    track = song.view.selected_track if song is not None else None
    if track is None:
      return "self.song().view.selected_track"
    tracks = list(getattr(song, "tracks", []) or [])
    if track in tracks:
      return f"self.song().tracks[{tracks.index(track)}]"
    return_tracks = list(getattr(song, "return_tracks", []) or [])
    if track in return_tracks:
      return f"self.song().return_tracks[{return_tracks.index(track)}]"
    master_track = getattr(song, "master_track", None)
    if track is master_track:
      return "self.song().master_track"
    return "self.song().view.selected_track"

  def _absolute_device_path(self, device):
    track_path = self._absolute_selected_track_path()
    if device is None:
      return f"{track_path}.view.selected_device"
    song = self.song()
    track = song.view.selected_track if song is not None else None
    if track is not None:
      device_path = self._device_path_string_in_container(track, device)
      if device_path:
        return f"{track_path}.{device_path}"
    return f"{track_path}.view.selected_device"

  def _device_path_string_in_container(self, container, target):
    if container is None or target is None:
      return ""
    devices = list(getattr(container, "devices", []) or [])
    for device_index, candidate in enumerate(devices):
      if candidate is target:
        return f"devices[{device_index}]"
      if getattr(candidate, "can_have_chains", False) or hasattr(candidate, "chains"):
        try:
          chains = list(getattr(candidate, "chains", []) or [])
        except Exception:
          chains = []
        for chain_index, chain in enumerate(chains):
          sub_path = self._device_path_string_in_container(chain, target)
          if sub_path:
            return f"devices[{device_index}].chains[{chain_index}].{sub_path}"
    return ""

  def _ascii7_bytes(self, text: str):
      """Converts a string to a list of 7-bit ASCII bytes."""
      return list((text or "").encode("ascii", "replace"))

  def test_method(self):
    self.log_message("csslog: it works!3")

  def send_time_signature(self):
    """
    Sends the current time signature (numerator and denominator) to TouchOSC via SysEx.
    Numerator: [240, 123, 8, <numerator>, 247]
    Denominator: [240, 123, 9, <denominator>, 247]
    """
    try:
      song = self.song()
      numerator = song.signature_numerator
      denominator = song.signature_denominator

      # Send numerator
      num_bytes = self._ascii7_bytes(str(numerator))
      sysex_numerator = [240, 123, 8] + num_bytes + [247]
      self._send_midi(tuple(sysex_numerator))
      self.log_message(f"csslog: Sent time signature numerator: {numerator}")

      # Send denominator
      den_bytes = self._ascii7_bytes(str(denominator))
      sysex_denominator = [240, 123, 9] + den_bytes + [247]
      self._send_midi(tuple(sysex_denominator))
      self.log_message(f"csslog: Sent time signature denominator: {denominator}")

    except Exception as e:
      self.log_message(f"csslog: Error sending time signature: {e}")

  def send_selected_device_name(self):
    """
        Sends the currently selected track name and device name as SysEx to TouchOSC.
        Format: [240, 123, 6, <track name ascii...>, 247]  -- Track name
                         [240, 123, 7, <device name ascii...>, 247] -- Device name
    """
    try:
      song = self.song()
      view = song.view if song is not None else None
      sel_track = view.selected_track if view is not None else None
      
      if sel_track is None:
        self.log_message("csslog: No selected track available")
        return
      
      # Send track name
      track_name = sel_track.name or ""
      track_sysex = [240, 123, 6] + [ord(c) for c in track_name] + [247]
      self._send_midi(tuple(track_sysex))
      self.log_message(f"csslog: Sent selected track name: '{track_name}'")
      
      # Send device name
      sel_device = sel_track.view.selected_device if hasattr(sel_track, 'view') else None
      if sel_device is not None:
        device_name = sel_device.name or ""
        device_sysex = [240, 123, 7] + [ord(c) for c in device_name] + [247]
        self._send_midi(tuple(device_sysex))
        self.log_message(f"csslog: Sent selected device name: '{device_name}'")
      else:
        device_name = "-------"
        device_sysex = [240, 123, 7] + [ord(c) for c in device_name] + [247]
        self._send_midi(tuple(device_sysex))
        self.log_message("csslog: No selected device available, sent placeholder")
        
    except Exception as e:
      self.log_message(f"csslog: Error sending selected track/device name: {e}")

  def has_selected_device(self, param_index=16, bank_size=16):
    """
    Returns 1 if the selected track has a selected device with parameters at
    param_index and its banked offsets (param_index + bank_size, ...), else 0.
    """
    try:
      if bank_size <= 0 or param_index < 0:
        return 0
      song = self.song()
      view = song.view if song is not None else None
      sel_track = view.selected_track if view is not None else None
      if sel_track is None:
        return 0
      sel_device = sel_track.view.selected_device if hasattr(sel_track, 'view') else None
      if sel_device is None:
        return 0
      params = getattr(sel_device, 'parameters', None)
      if not params or len(params) <= param_index:
        return 0
      for idx in range(param_index, len(params), bank_size):
        if params[idx] is None:
          return 0
      return 1
    except Exception:
      return 0

  def selected_device_params_changed(self, start_index=1, count=16):
    """
    Returns True if any selected device parameter value changed since last call.
    Checks parameters from start_index to start_index + count - 1 (default 1..16).
    """
    try:
      song = self.song()
      view = song.view if song is not None else None
      sel_track = view.selected_track if view is not None else None
      sel_device = sel_track.view.selected_device if (sel_track is not None and hasattr(sel_track, 'view')) else None
      if sel_device is None:
        self._last_selected_param_values = None
        self._last_selected_param_device = None
        return False
      params = getattr(sel_device, 'parameters', None)
      if not params:
        self._last_selected_param_values = None
        self._last_selected_param_device = sel_device
        return False

      if start_index < 0 or count <= 0:
        return False

      end_index = min(start_index + count, len(params))
      current_values = []
      for idx in range(start_index, end_index):
        try:
          current_values.append(params[idx].value)
        except Exception:
          current_values.append(None)

      changed = False
      if self._last_selected_param_device is not sel_device or self._last_selected_param_values is None:
        changed = True
      else:
        last_values = self._last_selected_param_values
        if len(last_values) != len(current_values):
          changed = True
        else:
          for old, new in zip(last_values, current_values):
            if old != new:
              changed = True
              break

      self._last_selected_param_values = current_values
      self._last_selected_param_device = sel_device
      return changed
    except Exception as e:
      self.log_message(f"csslog: Error checking selected device parameter changes: {e}")
      return False
  
  def send_selected_device_parameter_names(self):
    """
    Sends the parameter names of the selected device via SysEx to TouchOSC.
    Cycles through parameters 1 to 16 (or fewer if fewer parameters exist).
    For each parameter, sends: [240, 123, 5, <param_number>, <param_name_ascii...>, 247]
    If no parameters exist, sends '------' as placeholder for each slot.
    """
    try:
      song = self.song()
      view = song.view if song is not None else None
      sel_track = view.selected_track if view is not None else None
      
      if sel_track is None:
        self.log_message("csslog: No selected track available")
        return
      
      sel_device = sel_track.view.selected_device if hasattr(sel_track, 'view') else None
      if sel_device is None:
        self.log_message("csslog: No selected device available")
        return
      
      # Check if device has parameters
      if not hasattr(sel_device, 'parameters') or sel_device.parameters is None:
        self.log_message("csslog: Selected device has no parameters attribute")
        return
      
      num_parameters = len(sel_device.parameters)
      # self.log_message(f"csslog: Device has {num_parameters} parameters")
      
      # Send parameters 0 to 16
      for param_num in range(0, 17):
        
        if param_num < num_parameters:
          # Parameter exists, get its name
          try:
            param_name = sel_device.parameters[param_num].name or ""
          except Exception as e:
            self.log_message(f"csslog: Error reading parameter {param_num} name: {e}")
            param_name = ""
        else:
          # Parameter slot doesn't exist, use placeholder
          param_name = "------"
        
        # Send parameter name via SysEx
        sysex_message = [240, 123, 5, param_num] + [ord(c) for c in param_name] + [247]
        self._send_midi(tuple(sysex_message))
        # self.log_message(f"csslog: Sent parameter {param_num} name: '{param_name}'")
      
    except Exception as e:
      self.log_message(f"csslog: Error sending device parameter names: {e}")

  def send_selected_device_parameter_display(self, param_num):
    """
    Sends the selected device parameter display via SysEx.
    Format: [240, 123, 4, <param_number>, <display_ascii...>, 247]
    """
    try:
      song = self.song()
      view = song.view if song is not None else None
      sel_track = view.selected_track if view is not None else None

      if sel_track is None:
        self.log_message("csslog: No selected track available")
        return

      sel_device = sel_track.view.selected_device if hasattr(sel_track, 'view') else None
      if sel_device is None:
        self.log_message("csslog: No selected device available")
        return

      params = getattr(sel_device, 'parameters', None)
      if not params:
        self.log_message("csslog: Selected device has no parameters")
        return

      idx = int(param_num)
      if idx < 0 or idx >= len(params):
        display = "NONE"
      else:
        param = params[idx]
        if param is None:
          display = "NONE"
        else:
          try:
            if getattr(param, "is_quantized", False) and getattr(param, "value_items", None):
              value_items = list(param.value_items)
              value_index = int(param.value)
              if 0 <= value_index < len(value_items):
                display = value_items[value_index]
              else:
                display = param.str_for_value(param._str_)
            else:
              display = param.str_for_value(param.value)
          except Exception:
            display = str(param.value)

      sysex_message = [240, 123, 4, idx] + self._ascii7_bytes(display) + [247]
      self._send_midi(tuple(sysex_message))
      # self.log_message(f"csslog: Sent parameter {idx} display: '{display}'")

    except Exception as e:
      self.log_message(f"csslog: Error sending parameter display for {param_num}: {e}")
  
  def _get_sessionbox_context(self, sceneoff, trackoff):
    song = self.song()
    scene_idx = int(sceneoff)
    track_off = int(trackoff)

    if scene_idx < 0:
      self.log_message(f"csslog: Scene index negative: {scene_idx}")
      return None

    rows = 3
    clips_per_row = 8
    default_color = 27

    total_scenes = len(song.scenes) if hasattr(song, 'scenes') else 0
    total_tracks = len(song.tracks) if hasattr(song, 'tracks') else 0

    return (song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color)

  def _clamp_color_index(self, value, default_color):
    try:
      idx = int(value) if value is not None else default_color
    except Exception:
      idx = default_color
    if idx < 0:
      idx = 0
    if idx > 69:
      idx = 69
    return idx

  def _build_nul_separated_payload(self, names):
    payload = []
    last_index = len(names) - 1
    for idx, name in enumerate(names):
      payload.extend(self._ascii7_bytes(name))
      if idx < last_index:
        payload.append(0)
    return payload

  def send_sessionbox_scene_names(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_scene_names(ctx)

  def _send_sessionbox_scene_names(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    for row in range(rows):
      row_scene = scene_idx + row

      if 0 <= row_scene < total_scenes:
        scene_name = song.scenes[row_scene].name or ""
      else:
        scene_name = ""

      rn = int(row) if 0 <= row < rows else 0
      if row < 0 or row >= rows:
        self.log_message(f"csslog: Invalid scene row {row}, sending 0 as row byte")
      sysex_scene = [240, 126, 5, rn] + self._ascii7_bytes(scene_name) + [247]
      self._send_midi(tuple(sysex_scene))
      self.log_message(f"csslog: Sent scene name for row {row} (scene_index {row_scene}): '{scene_name}'")

  def send_sessionbox_scene_colors(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_scene_colors(ctx)

  def _send_sessionbox_scene_colors(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    for row in range(rows):
      row_scene = scene_idx + row
      val = None
      try:
        if 0 <= row_scene < total_scenes:
          val = song.scenes[row_scene].color_index
      except Exception as e:
        self.log_message(f"csslog: Error reading scene color for scene {row_scene}: {e}")

      scene_color_idx = self._clamp_color_index(val, default_color)
      rn = int(row) if 0 <= row < rows else 0
      sysex_scene_color = [240, 126, 8, rn, scene_color_idx, 247]
      self._send_midi(tuple(sysex_scene_color))

  def send_sessionbox_clip_colors(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_clip_colors(ctx)

  def _send_sessionbox_clip_colors(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    for row in range(rows):
      row_scene = scene_idx + row
      clip_color_indices = []
      for i in range(clips_per_row):
        track_idx = track_off + i
        val = None
        try:
          if 0 <= track_idx < total_tracks:
            track = song.visible_tracks[track_idx]
            if hasattr(track, 'clip_slots') and 0 <= row_scene < len(track.clip_slots):
              slot = track.clip_slots[row_scene]
              if slot and getattr(slot, 'has_clip', False) and getattr(slot, 'clip', None) is not None:
                val = getattr(slot.clip, 'color_index', None)
        except Exception as e:
          self.log_message(f"csslog: Error reading clip color (t{track_idx}, s{row_scene}): {e}")

        clip_color_indices.append(self._clamp_color_index(val, default_color))

      rn = int(row) if 0 <= row < rows else 0
      sysex_clip_colors_bulk = [240, 126, 7, rn] + clip_color_indices + [247]
      self._send_midi(tuple(sysex_clip_colors_bulk))

  def send_sessionbox_clip_names(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_clip_names(ctx)

  def _send_sessionbox_clip_names(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    for row in range(rows):
      row_scene = scene_idx + row
      clip_names = []
      for i in range(clips_per_row):
        track_idx = track_off + i
        name = ""
        try:
          if 0 <= track_idx < total_tracks:
            track = song.visible_tracks[track_idx]
            if hasattr(track, 'clip_slots') and 0 <= row_scene < len(track.clip_slots):
              slot = track.clip_slots[row_scene]
              if slot and getattr(slot, 'has_clip', False) and getattr(slot, 'clip', None) is not None:
                name = slot.clip.name or ""
        except Exception as e:
          self.log_message(f"csslog: Error reading clip name (t{track_idx}, s{row_scene}): {e}")
          name = ""
        clip_names.append(name)

      payload_clips = self._build_nul_separated_payload(clip_names)
      rn = int(row) if 0 <= row < rows else 0
      sysex_clips = [240, 126, 4, rn] + payload_clips + [247]
      self._send_midi(tuple(sysex_clips))

  def send_sessionbox_track_colors(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_track_colors(ctx)

  def _send_sessionbox_track_colors(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    color_indices = []
    visible_count = len(song.visible_tracks) if hasattr(song, 'visible_tracks') else total_tracks
    try:
      return_tracks = list(song.return_tracks)
    except Exception:
      return_tracks = []
    try:
      visible_offset = self.track_num(0)
    except Exception:
      visible_offset = track_off
    if visible_offset < 0:
      visible_offset = 0
    visible_remaining = max(0, visible_count - visible_offset)

    for i in range(8):
      val = None
      try:
        if i < visible_remaining:
          ti = self.track_num(i)
          if 0 <= ti < visible_count:
            val = song.visible_tracks[ti].color_index
        else:
          rt_idx = i - visible_remaining
          if 0 <= rt_idx < len(return_tracks):
            val = return_tracks[rt_idx].color_index
      except Exception:
        val = None
      color_indices.append(self._clamp_color_index(val, default_color))

    master_val = None
    try:
      master_val = self.song().master_track.color_index
    except Exception:
      master_val = None
    color_indices.append(self._clamp_color_index(master_val, default_color))

    sysex_colors = [240, 126, 1] + color_indices + [247]
    self._send_midi(tuple(sysex_colors))

  def send_sessionbox_track_names(self, sceneoff, trackoff):
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_track_names(ctx)

  def _send_sessionbox_track_names(self, ctx):
    song, scene_idx, track_off, total_scenes, total_tracks, rows, clips_per_row, default_color = ctx
    track_names = []
    visible_count = len(song.visible_tracks) if hasattr(song, 'visible_tracks') else total_tracks
    try:
      return_tracks = list(song.return_tracks)
    except Exception:
      return_tracks = []
    try:
      visible_offset = self.track_num(0)
    except Exception:
      visible_offset = track_off
    if visible_offset < 0:
      visible_offset = 0
    visible_remaining = max(0, visible_count - visible_offset)

    for i in range(8):
      tn = ""
      try:
        if i < visible_remaining:
          track_idx = self.track_num(i)
          if 0 <= track_idx < visible_count:
            tn = song.visible_tracks[track_idx].name or f"Track {track_idx+1}"
        else:
          rt_idx = i - visible_remaining
          if 0 <= rt_idx < len(return_tracks):
            tn = return_tracks[rt_idx].name or f"Return {rt_idx+1}"
      except Exception as e:
        tn = ""
        self.log_message(f"csslog: Error reading track name {i}: {e}")
      track_names.append(tn)

    payload_tracks = self._build_nul_separated_payload(track_names)
    sysex_tracks = [240, 126, 2] + payload_tracks + [247]
    self._send_midi(tuple(sysex_tracks))

  def send_sessionbox_snapshot(self, sceneoff, trackoff):
    """
    Updated for 3-row session box where each row contains:
      - 8 clip slots (per-row clip buttons)
      - 1 scene button (sent separately)
    Sends for three rows (sceneoff..sceneoff+2):
      - Scene name    (F0 7E 05 <ascii...> F7)  -- one per row
      - Clip colors   (F0 7E 07 <c0..c7> F7)    -- one per row (8 clips)
      - Clip names    (F0 7E 04 <n1\0..n8> F7)  -- one per row (8 NUL-separated)
      - Track colors  (F0 7E 01 <c0..cN-1> F7)  -- visible tracks (unchanged)
      - Track names   (F0 7E 02 <t1\0..t8> F7)  -- unchanged
    """
    ctx = self._get_sessionbox_context(sceneoff, trackoff)
    if not ctx:
      return
    self._send_sessionbox_scene_names(ctx)
    self._send_sessionbox_scene_colors(ctx)
    self._send_sessionbox_clip_colors(ctx)
    self._send_sessionbox_clip_names(ctx)
    self._send_sessionbox_track_colors(ctx)
    self._send_sessionbox_track_names(ctx)
      
  def _inputs(self):
    self.input_map = [
      "midi_cc_ch_15_val_1",
      "midi_cc_ch_15_val_2",
      "midi_cc_ch_15_val_4",
      "midi_cc_ch_15_val_3",
      "midi_cc_ch_15_val_8",
      "midi_cc_ch_15_val_7",
      "midi_cc_ch_15_val_5",
      "midi_cc_ch_15_val_6",
      "midi_cc_ch_15_val_10",
      "midi_cc_ch_15_val_11",
      "midi_cc_ch_15_val_12",
      "midi_cc_ch_15_val_13",
      "midi_cc_ch_15_val_14",
      "midi_cc_ch_15_val_15",
      "midi_cc_ch_15_val_16",
      "midi_cc_ch_15_val_17",
      "midi_cc_ch_15_val_18",
      "midi_cc_ch_15_val_23",
      "midi_cc_ch_15_val_24",
      "midi_cc_ch_15_val_25",
      "midi_cc_ch_15_val_22",
      "midi_cc_ch_15_val_21",
      "midi_cc_ch_15_val_20",
      "midi_cc_ch_15_val_19",
      "midi_cc_ch_15_val_26",
      "midi_cc_ch_15_val_27",
      "midi_cc_ch_15_val_29",
      "midi_cc_ch_15_val_28",
      "midi_cc_ch_15_val_30",
      "midi_cc_ch_15_val_9",
      "midi_cc_ch_15_val_31",
      "midi_cc_ch_15_val_32",
      "midi_cc_ch_15_val_33",
      "midi_cc_ch_15_val_34",
      "midi_cc_ch_15_val_35",
      "midi_cc_ch_15_val_36",
      "midi_cc_ch_15_val_60",
      "midi_cc_ch_15_val_61",
      "midi_cc_ch_15_val_62",
      "midi_cc_ch_15_val_59",
      "midi_cc_ch_1_val_41",
      "midi_cc_ch_15_val_73",
      "midi_cc_ch_15_val_120",
      "midi_cc_ch_15_val_74",
      "midi_cc_ch_15_val_75",
      "midi_cc_ch_15_val_76",
      "midi_cc_ch_15_val_77",
      "midi_cc_ch_15_val_78",
      "midi_cc_ch_15_val_79",
      "midi_cc_ch_15_val_80",
      "midi_cc_ch_15_val_68",
      "midi_cc_ch_15_val_69",
      "midi_cc_ch_15_val_70",
      "midi_cc_ch_15_val_71",
      "midi_cc_ch_15_val_72",
      "midi_cc_ch_15_val_66",
      "midi_cc_ch_15_val_67",
      "midi_cc_ch_15_val_65",
      "midi_cc_ch_14_val_16",
      "midi_cc_ch_0_val_7",
      "midi_cc_ch_1_val_7",
      "midi_cc_ch_2_val_7",
      "midi_cc_ch_4_val_7",
      "midi_cc_ch_5_val_7",
      "midi_cc_ch_3_val_7",
      "midi_cc_ch_7_val_7",
      "midi_cc_ch_6_val_7",
      "midi_cc_ch_14_val_0",
      "midi_cc_ch_14_val_1",
      "midi_cc_ch_14_val_2",
      "midi_cc_ch_14_val_3",
      "midi_cc_ch_14_val_4",
      "midi_cc_ch_14_val_5",
      "midi_cc_ch_14_val_6",
      "midi_cc_ch_14_val_7",
      "midi_cc_ch_14_val_13",
      "midi_cc_ch_14_val_14",
      "midi_cc_ch_14_val_15",
      "midi_cc_ch_14_val_9",
      "midi_cc_ch_14_val_10",
      "midi_cc_ch_14_val_11",
      "midi_cc_ch_14_val_12",
      "midi_cc_ch_14_val_8",
      "midi_cc_ch_15_val_55",
      "midi_cc_ch_15_val_57",
      "midi_cc_ch_15_val_58",
      "midi_cc_ch_15_val_38",
      "midi_cc_ch_15_val_39",
      "midi_cc_ch_15_val_40",
      "midi_cc_ch_15_val_41",
      "midi_cc_ch_15_val_42",
      "midi_cc_ch_15_val_43",
      "midi_cc_ch_15_val_44",
      "midi_cc_ch_15_val_45",
      "midi_cc_ch_15_val_37",
      "midi_cc_ch_15_val_47",
      "midi_cc_ch_15_val_48",
      "midi_cc_ch_15_val_49",
      "midi_cc_ch_15_val_50",
      "midi_cc_ch_15_val_51",
      "midi_cc_ch_15_val_52",
      "midi_cc_ch_15_val_53",
      "midi_cc_ch_15_val_54",
      "midi_cc_ch_15_val_46",
      "midi_cc_ch_15_val_56",
      "midi_cc_ch_15_val_88",
      "midi_cc_ch_15_val_87",
      "midi_cc_ch_15_val_86",
      "midi_cc_ch_15_val_85",
      "midi_cc_ch_15_val_84",
      "midi_cc_ch_15_val_83",
      "midi_cc_ch_15_val_82",
      "midi_cc_ch_15_val_81",
      "midi_cc_ch_15_val_89",
      "midi_cc_ch_15_val_106",
      "midi_cc_ch_15_val_107",
      "midi_cc_ch_15_val_108",
      "midi_cc_ch_15_val_109",
      "midi_cc_ch_15_val_110",
      "midi_cc_ch_15_val_113",
      "midi_cc_ch_15_val_112",
      "midi_cc_ch_15_val_111",
      "midi_cc_ch_15_val_98",
      "midi_cc_ch_15_val_99",
      "midi_cc_ch_15_val_100",
      "midi_cc_ch_15_val_101",
      "midi_cc_ch_15_val_102",
      "midi_cc_ch_15_val_103",
      "midi_cc_ch_15_val_105",
      "midi_cc_ch_15_val_104",
      "midi_cc_ch_15_val_90",
      "midi_cc_ch_15_val_91",
      "midi_cc_ch_15_val_92",
      "midi_cc_ch_15_val_93",
      "midi_cc_ch_15_val_94",
      "midi_cc_ch_15_val_95",
      "midi_cc_ch_15_val_96",
      "midi_cc_ch_15_val_97",
      "midi_cc_ch_15_val_115",
      "midi_cc_ch_15_val_114",
      "midi_cc_ch_15_val_116",
      "midi_cc_ch_15_val_119",
      "midi_cc_ch_15_val_118",
      "midi_cc_ch_15_val_122",
      "midi_cc_ch_9_val_121",
      "midi_cc_ch_15_val_125",
      "midi_cc_ch_15_val_124",
      "midi_cc_ch_14_val_17",
      "midi_cc_ch_14_val_18",
      "midi_cc_ch_14_val_20",
      "midi_cc_ch_14_val_19",
      "midi_cc_ch_14_val_21",
      "midi_cc_ch_14_val_22",
      "midi_cc_ch_14_val_24",
      "midi_cc_ch_14_val_23",
      "midi_cc_ch_14_val_25",
      "midi_cc_ch_14_val_26",
      "midi_cc_ch_14_val_27",
      "midi_cc_ch_14_val_28",
      "midi_cc_ch_14_val_30",
      "midi_cc_ch_14_val_31",
      "midi_cc_ch_14_val_29",
      "midi_cc_ch_14_val_32",
      "midi_cc_ch_14_val_33",
      "midi_cc_ch_14_val_34",
      "midi_cc_ch_14_val_35",
      "midi_cc_ch_14_val_36",
      "midi_cc_ch_14_val_37",
      "midi_cc_ch_14_val_38",
      "midi_cc_ch_15_val_117",
      "midi_cc_ch_15_val_121"]
