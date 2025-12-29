from __future__ import absolute_import, print_function, unicode_literals

"""
Drop this module into `user.py` to get Push-style nested rack navigation that you
can drive from Control Surface Studio / TouchOSC.

Only the built-in Live API modules are imported (``Live`` and
``ableton.v2.base``), so it works with the standard Mac/Windows Live install
without extra dependencies.

Usage sketch (inside your CSS callbacks):

    nav = NavigationManager(song)

    # Always call this when the selected track/device changes
    def refresh_from_live(*_):
        nav.refresh(song.view.selected_track.view.selected_device or song)
        send_ui(nav.names(), nav.current_node.selected_child)

    # Map the following to MIDI buttons/gestures
    def nav_up(value, *_):
        if value:  # button down
            nav.bump_selection(-1)
            send_ui(nav.names(), nav.current_node.selected_child)

    def nav_down(value, *_):
        if value:
            nav.bump_selection(1)
            send_ui(nav.names(), nav.current_node.selected_child)

    def nav_enter(value, *_):
        if value:
            nav.enter()
            send_ui(nav.names(), nav.current_node.selected_child)

    def nav_back(value, *_):
        if value:
            nav.exit()
            send_ui(nav.names(), nav.current_node.selected_child)

    def nav_toggle(value, *_):
        if value:
            nav.toggle_selected()
            send_ui(nav.names(), nav.current_node.selected_child)

`send_ui` would push the node names/state to your TouchOSC layout. The helper
methods on `NavigationManager` below are the ones to map in CSS: `refresh`,
`bump_selection`, `enter`, `exit`, `toggle_selected`, `select_index`, plus the
`names()`/`states()` accessors for populating your controls.
"""

import Live
from ableton.v2.base import EventObject, listenable_property, listens, liveobj_valid


def _as_list(obj):
    return list(obj) if obj else []


class NavigationNode(EventObject):
    __events__ = ("children", "selected_child", "state")

    @property
    def children(self):
        return self._children

    @property
    def selected_child(self):
        return self._selected_child

    @selected_child.setter
    def selected_child(self, index):
        if index is None:
            self._selected_child = None
            self._set_selected_child_in_model(None)
        elif 0 <= index < len(self._children):
            _, obj = self._children[index]
            self._selected_child = index
            self._set_selected_child_in_model(obj)
        self.notify_selected_child(self._selected_child)

    @property
    def state(self):
        return self._state

    def set_state(self, index, value):
        if 0 <= index < len(self._children):
            _, obj = self._children[index]
            self._state[index] = self._set_state_in_model(obj, value)
            self.notify_state(index, self._state[index])

    @property
    def object(self):
        return self._object

    @property
    def parent(self):
        return self._parent

    def preselect(self):
        if self._selected_child is None and self._children:
            self.selected_child = 0

    # --- hooks for subclasses -------------------------------------------------
    def _set_selected_child_in_model(self, child):
        pass

    def _set_state_in_model(self, child, value):
        return value


class ModelNode(NavigationNode):
    def __init__(self, object=None, parent=None, *a, **k):
        super().__init__(*a, **k)
        self._object = object
        self._parent = parent
        self._children = []
        self._state = []
        self._selected_child = None
        self._in_update_children = False
        self._children = self._get_children_from_model()
        self._state = [self._get_state_from_model(obj) for _, obj in self._children]
        self._update_selected_child()

    def _get_children_from_model(self):
        return []

    def _get_selected_child_from_model(self):
        return None

    def _set_selected_child_in_model(self, child):
        pass

    def _get_state_from_model(self, child):
        return 0

    def _set_state_in_model(self, child, value):
        return value

    def _update_selected_child(self):
        selected = self._get_selected_child_from_model()
        children = [c[1] for c in self._children]
        self._selected_child = children.index(selected) if selected in children else None


class SongNode(ModelNode):
    def _get_children_from_model(self):
        song = self._object
        entries = [(t.name, t) for t in song.tracks]
        return entries

    def _get_selected_child_from_model(self):
        return self._object.view.selected_track

    def _set_selected_child_in_model(self, child):
        if liveobj_valid(child):
            self._object.view.selected_track = child


class TrackNode(ModelNode):
    def _get_children_from_model(self):
        track = self._object
        devices = [(d.name, d) for d in _as_list(track.devices)]
        if track.view.selected_chain:
            devices.insert(0, ("Selected Chain", track.view.selected_chain))
        return devices

    def _get_selected_child_from_model(self):
        return self._object.view.selected_device

    def _set_selected_child_in_model(self, child):
        if liveobj_valid(child):
            self._object.view.select_device(child)


class ChainNode(ModelNode):
    class RackBank2Device(object):
        def __init__(self, rack_device):
            self.rack_device = rack_device

    def _get_children_from_model(self):
        chain = self._object
        children = []
        for device in _as_list(chain.devices):
            children.append((device.name, device))
            if device.can_have_chains and not device.can_have_drum_pads:
                children.append(("{} (Macros 9-16)".format(device.name), ChainNode.RackBank2Device(device)))
            if device.can_have_drum_pads and device.view.selected_drum_pad:
                pad = device.view.selected_drum_pad
                if pad.chains:
                    children.append(("Pad: {}".format(pad.name), pad.chains[0]))
        return children

    def _get_selected_child_from_model(self):
        return self._object.canonical_parent.view.selected_device

    def _set_selected_child_in_model(self, child):
        if liveobj_valid(child):
            self._object.canonical_parent.view.select_device(child)

    def _get_state_from_model(self, child):
        if hasattr(child, "is_enabled"):
            return int(child.is_enabled)
        return 0

    def _set_state_in_model(self, child, value):
        if hasattr(child, "is_enabled"):
            child.is_enabled = bool(value)
        return int(bool(value))


class RackNode(ModelNode):
    def _get_children_from_model(self):
        rack = self._object
        return [(chain.name or "Chain", chain) for chain in _as_list(rack.chains)]

    def _get_selected_child_from_model(self):
        return self._object.view.selected_chain

    def _set_selected_child_in_model(self, child):
        if liveobj_valid(child):
            self._object.view.selected_chain = child


class SimpleDeviceNode(ModelNode):
    def _get_children_from_model(self):
        return []

    def _get_state_from_model(self, child):
        if hasattr(child, "is_enabled"):
            return int(child.is_enabled)
        return 0

    def _set_state_in_model(self, child, value):
        if hasattr(child, "is_enabled"):
            child.is_enabled = bool(value)
        return int(bool(value))


def make_navigation_node(model_object, parent=None, is_entering=True):
    if isinstance(model_object, ChainNode.RackBank2Device):
        model_object = model_object.rack_device

    if model_object is None:
        return None
    if isinstance(model_object, Live.Song.Song):
        return SongNode(model_object, parent=parent)
    if isinstance(model_object, Live.Track.Track):
        return TrackNode(model_object, parent=parent)
    if isinstance(model_object, Live.Chain.Chain):
        return ChainNode(model_object, parent=parent)
    if isinstance(model_object, Live.DrumPad.DrumPad):
        if model_object.chains:
            return ChainNode(model_object.chains[0], parent=parent)
        return None
    if isinstance(model_object, Live.Device.Device):
        if model_object.can_have_chains:
            if model_object.can_have_drum_pads:
                if is_entering:
                    return None
                return make_navigation_node(model_object.canonical_parent, parent=parent, is_entering=is_entering)
            return RackNode(model_object, parent=parent)
        return SimpleDeviceNode(model_object, parent=parent)
    return None


class NavigationManager(EventObject):
    """Minimal Push-like navigator you can drive from CSS triggers."""

    def __init__(self, song):
        super().__init__()
        self._song = song
        self._current_node = None
        self.refresh(song)

    @listenable_property
    def current_node(self):
        return self._current_node

    def refresh(self, model_object):
        self._current_node = make_navigation_node(model_object)
        if self._current_node:
            self._current_node.preselect()
            self.notify_current_node()
        return self._current_node

    def enter(self):
        if not self._current_node or self._current_node.selected_child is None:
            return self._current_node
        name, child_obj = self._current_node.children[self._current_node.selected_child]
        next_node = make_navigation_node(child_obj, parent=self._current_node)
        if next_node:
            self._current_node = next_node
            self._current_node.preselect()
            self.notify_current_node()
        return self._current_node

    def exit(self):
        if self._current_node and self._current_node.parent:
            self._current_node = self._current_node.parent
            self.notify_current_node()
        return self._current_node

    def bump_selection(self, delta):
        if not self._current_node:
            return
        if self._current_node.selected_child is None:
            self._current_node.preselect()
        else:
            new_index = max(0, min(len(self._current_node.children) - 1, self._current_node.selected_child + delta))
            self._current_node.selected_child = new_index
        self.notify_current_node()

    def select_index(self, index):
        if self._current_node:
            self._current_node.selected_child = index
            self.notify_current_node()

    def toggle_index(self, index, value):
        if self._current_node:
            self._current_node.set_state(index, value)

    def toggle_selected(self):
        if self._current_node and self._current_node.selected_child is not None:
            idx = self._current_node.selected_child
            current = 0
            if idx < len(self._current_node.state):
                current = self._current_node.state[idx]
            self._current_node.set_state(idx, 0 if current else 1)

    def names(self):
        return [name for name, _ in self._current_node.children] if self._current_node else []

    def states(self):
        return list(self._current_node.state) if self._current_node else []

    @listens("selected_track")
    def _on_selected_track(self):
        self.refresh(self._song.view.selected_track)

