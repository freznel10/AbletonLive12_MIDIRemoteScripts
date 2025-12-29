-- ===== Ableton Live colors (0..69) as RGBA floats (0..1) =====
LIVE_COLOR = {                                 -- Table mapping Ableton color index → RGBA color in 0..1 floats
  [0]={0.969,0.494,0.588,1.000},[1]={0.973,0.580,0.129,1.000},[2]={0.749,0.537,0.118,1.000},
  [3]={0.965,0.961,0.416,1.000},[4]={0.710,1.000,0.027,1.000},[5]={0.267,1.000,0.141,1.000},
  [6]={0.263,1.000,0.596,1.000},[7]={0.325,1.000,0.886,1.000},[8]={0.482,0.718,1.000,1.000},
  [9]={0.267,0.408,0.867,1.000},[10]={0.502,0.576,1.000,1.000},[11]={0.808,0.306,0.867,1.000},
  [12]={0.863,0.216,0.561,1.000},[13]={1.000,1.000,1.000,1.000},[14]={0.957,0.106,0.165,1.000},
  [15]={0.949,0.337,0.039,1.000},[16]={0.529,0.369,0.227,1.000},[17]={1.000,0.941,0.161,1.000},
  [18]={0.478,1.000,0.333,1.000},[19]={0.212,0.733,0.004,1.000},[20]={0.176,0.706,0.624,1.000},
  [21]={0.220,0.898,0.996,1.000},[22]={0.129,0.569,0.914,1.000},[23]={0.090,0.408,0.698,1.000},
  [24]={0.455,0.318,0.867,1.000},[25]={0.651,0.369,0.729,1.000},[26]={0.949,0.024,0.792,1.000},
  [27]={0.776,0.776,0.776,1.000},[28]={0.847,0.314,0.286,1.000},[29]={0.973,0.569,0.380,1.000},
  [30]={0.784,0.616,0.369,1.000},[31]={0.914,1.000,0.624,1.000},[32]={0.788,0.878,0.525,1.000},
  [33]={0.678,0.788,0.380,1.000},[34]={0.541,0.729,0.482,1.000},[35]={0.796,0.996,0.855,1.000},
  [36]={0.765,0.933,0.965,1.000},[37]={0.671,0.698,0.863,1.000},[38]={0.757,0.671,0.867,1.000},
  [39]={0.616,0.506,0.875,1.000},[40]={0.875,0.827,0.855,1.000},[41]={0.596,0.596,0.596,1.000},
  [42]={0.722,0.494,0.471,1.000},[43]={0.659,0.431,0.267,1.000},[44]={0.525,0.439,0.341,1.000},
  [45]={0.702,0.682,0.337,1.000},[46]={0.592,0.710,0.020,1.000},[47]={0.424,0.643,0.239,1.000},
  [48]={0.471,0.714,0.671,1.000},[49]={0.541,0.643,0.718,1.000},[50]={0.455,0.576,0.706,1.000},
  [51]={0.447,0.498,0.753,1.000},[52]={0.580,0.506,0.651,1.000},[53]={0.694,0.549,0.694,1.000},
  [54]={0.682,0.353,0.518,1.000},[55]={0.408,0.408,0.408,1.000},[56]={0.616,0.129,0.153,1.000},
  [57]={0.592,0.243,0.145,1.000},[58]={0.373,0.243,0.196,1.000},[59]={0.831,0.725,0.027,1.000},
  [60]={0.455,0.525,0.094,1.000},[61]={0.267,0.569,0.145,1.000},[62]={0.137,0.553,0.486,1.000},
  [63]={0.114,0.314,0.443,1.000},[64]={0.082,0.114,0.518,1.000},[65]={0.141,0.239,0.565,1.000},
  [66]={0.314,0.204,0.616,1.000},[67]={0.573,0.196,0.612,1.000},[68]={0.745,0.082,0.357,1.000},
  [69]={0.184,0.180,0.180,1.000},
}

-- Global helper: return a Color() from a LIVE_COLOR index (0..69).
-- Usage: local c = LiveColorFromIndex(27); if c then ctrl.color = c end
function LiveColorFromIndex(index)
  local c = LIVE_COLOR[index]
  if c then
    return Color(c[1], c[2], c[3], c[4])
  end
  return nil
end

local NEUTRAL_IDX    = 27                    -- Fallback color index (a neutral grey)
local CURRENT_OFFSET = 0                     -- Kept for legacy color path / mapping (not used by bulk names)
-- === Radio group for ChainButtons (CH16, CC120, value 0..19) ===

local CC_CH16   = MIDIMessageType.CONTROLCHANGE + 15  -- 0xB0 + 15 = 191
local CC_NUM    = 120                                 -- Controller number
local CHAIN_MIN = 0
local CHAIN_MAX = 19
local current_chain_idx = nil
-- IN: Channel 2 CC41
local CC41_CH2 = MIDIMessageType.CONTROLCHANGE + 1  -- ch2
local CC41_NUM = 41

-- 17 keys (radio indices 0..16)
local SONG_KEYS = {
  "C","C#","Db","D","D#","Eb","E","F","F#","Gb","G","G#","Ab","A","A#","Bb","B"
}

-- RECEIVE mapping: your observed upper-bounds for each key bucket
-- (covers 0..127 continuously; note we include 35 into the D# bucket to avoid a gap)
local SONG_KEY_UPPER = {
  3,   -- C   0..3
  9,   -- C#  4..9
  19,  -- Db  10..19
  27,  -- D   20..27
  35,  -- D#  28..35  (fills the "35" gap)
  43,  -- Eb  36..43
  51,  -- E   44..51
  59,  -- F   52..59
  67,  -- F#  60..67
  75,  -- Gb  68..75
  83,  -- G   76..83
  91,  -- G#  84..91
  99,  -- Ab  92..99
  107, -- A   100..107
  115, -- A#  108..115
  123, -- Bb  116..123
  127, -- B   124..127
}

-- SEND mapping: YOU control this (midpoints, or anything you want to transmit)
local SONG_KEY_SEND_VALUES = {
  2, 7, 15, 24, 31, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 126
}

-- feedback guard so incoming MIDI doesn't re-trigger outgoing MIDI
songKeyUpdatingFromMidi = false

local function clamp(v, lo, hi)
  if v < lo then return lo end
  if v > hi then return hi end
  return v
end

-- Convert ANY received CC value (0..127) into radio index 0..16 using upper-bound buckets
local function ccValueToSongKeyIndex0(v)
  v = clamp(tonumber(v) or 0, 0, 127)
  for i, ub in ipairs(SONG_KEY_UPPER) do
    if v <= ub then
      return i - 1  -- 0-based index
    end
  end
  return 16
end

-- Adjust this getter to your actual control path/name
local function getSongKeySelector()
  local p = root.children.pager1
  local page = p and p.children.MAIN
  return page and page.children.SongKeySelector
end

local function getSongKeyLabel()
  local p = root.children.pager1
  local page = p and p.children.MAIN
  return page and page.children.SongKeyLabel
end

-- ===== Helpers =====
local function setColorFromTable(ctrl, index) -- Apply a LIVE_COLOR index to a control’s .color
  local c = LIVE_COLOR[index]
  if c then ctrl.color = Color(c[1], c[2], c[3], c[4]) end
end


local function getTempoLabel()
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  return page.children.TempoLabel
end

-- Getter for SelectedDevice label in pager1.MAIN
local function getSelectedDeviceLabel()
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  return page.children.SelectedDevice
end

-- Getter for SelectedTrack label in pager1.MAIN
local function getSelectedTrackLabel()
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  return page.children.SelectedTrack
end

-- Getter for Numerator label in pager1.MAIN (similar to TempoLabel)
local function getNumeratorLabel()
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  return page.children.Numerator
end

-- Getter for Denominator label in pager1.MAIN (similar to TempoLabel)
local function getDenominatorLabel()
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  return page.children.Denominator
end

-- Getter for Device Parameter Name label in pager1.MAIN.ControlPager.Device.SelectedDeviceParameterNames
local function getDeviceParameterNameLabel(param_num)
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  local pager = page.children.ControlPager
  if not pager then return nil end
  local device = pager.children.Device
  if not device then return nil end
  local group = device.children.SelectedDeviceParameterNames
  if not group then return nil end
  return group.children["label" .. tostring(param_num)]
end

-- Getter for Device Parameter Value label in pager1.MAIN.ControlPager.Device.SelectedDeviceParameterNames
local function getDeviceParameterValueLabel(param_num)
  local p = root.children.pager1
  if not p then return nil end
  local page = p.children.MAIN
  if not page then return nil end
  local pager = page.children.ControlPager
  if not pager then return nil end
  local device = pager.children.Device
  if not device then return nil end
  local group = device.children.SelectedDeviceParameterNames
  if not group then return nil end
  return group.children["valuelabel" .. tostring(param_num)]
end

local function getFader(zcol0)               -- Get fader0..fader8 by zero-based column
  local p = root.children.pager1             -- Root → pager1
  local page = p and p.children.MAIN         -- pager1 → MAIN page
  local grp  = page and page.children.FaderGroup1 -- MAIN → group containing the faders
  return grp and grp.children["fader" .. tostring(zcol0)] -- Return fader control by name
end

local function getTrackNameLabel(zcol0)      -- Get TrackName1..8 by zero-based column
  local p = root.children.pager1
  local page = p and p.children.MAIN
  local grp  = page and page.children.TrackNameText
  return grp and grp.children["TrackName" .. tostring(zcol0 + 1)]
end

-- NOTE: supports 0..8 (ClipName8 is the Scene Name)
local function getClipNameLabel(zcol0)       -- Get ClipName0..8 (8 is used for scene name)
  local p = root.children.pager1
  local page = p and p.children.MAIN
  local grp  = page and page.children.ClipNameLabel1
  return grp and grp.children["ClipName" .. tostring(zcol0)]
end

-- SessBoxClip buttons (Clip0..Clip7)
local function getSessBoxClipButton(zcol0)
  local p = root.children.pager1
  local page = p and p.children.MAIN
  local grp  = page and page.children.SessBoxClip
  return grp and grp.children["Clip" .. tostring(zcol0)]
end


local function clearClipNames_0_7()          -- Clear ClipName0..7 (avoid stale text)
  for i = 0, 7 do
    local L = getClipNameLabel(i)
    if L then L.values.text = "" end
  end
end

local function clearTrackNames_0_7()         -- Clear TrackName0..7 (optional tidiness)
  for i = 0, 7 do
    local L = getTrackNameLabel(i)
    if L then L.values.text = "" end
  end
end

local function resetFaders()                 -- Reset all fader colors to neutral
  for i = 0, 8 do
    local f = getFader(i)
    if f then setColorFromTable(f, NEUTRAL_IDX) end
  end
end

-- moved: robust parse_names_from_bytes is defined here (outside onReceiveMIDI)
local function parse_names_from_bytes(msg, start_idx, end_idx)
  local names = {}
  if not msg then return names end

  local msg_len = (#msg)
  local is_string = (type(msg) == "string")
  local is_table  = (type(msg) == "table")

  start_idx = math.max(1, tonumber(start_idx) or 1)
  end_idx   = tonumber(end_idx) or msg_len
  end_idx   = math.min(end_idx, msg_len)

  if start_idx > end_idx then return names end

  local function byte_at(i)
    if is_string then
      return msg:byte(i) or 0
    elseif is_table then
      return msg[i] or 0
    else
      return 0
    end
  end

  -- detect NUL (0) separators in the range
  local has_nul = false
  for i = start_idx, end_idx do
    if byte_at(i) == 0 then has_nul = true break end
  end

  if has_nul then
    local cur = ""
    for i = start_idx, end_idx do
      local b = byte_at(i)
      if b == 0 then
        table.insert(names, cur)
        cur = ""
      else
        cur = cur .. string.char(b)
      end
    end
    table.insert(names, cur) -- last token (may be empty)
  else
    local all = ""
    for i = start_idx, end_idx do all = all .. string.char(byte_at(i)) end
    local sep = "|"
    local found = false
    for token in string.gmatch(all, "([^" .. sep .. "]+)") do
      table.insert(names, token)
      found = true
    end
    if not found then table.insert(names, all) end
  end

  return names
end

-- ===== Clip Button / ClipName helpers (updated for 3-row session box: 0..26) =====
local CLIP_COLOR_PTR = 0  -- cycles 0..7 (legacy pointer kept)
local CLIP_NAMES_ROW_PTR = 0    -- rotates 0..2 for incoming 126,4 messages (row 0..2)
local CLIP_COLORS_ROW_PTR = 0   -- rotates 0..2 for incoming 126,7 messages (row 0..2)
local SCENE_ROW_PTR = 0         -- rotates 0..2 for incoming 126,5 messages (row 0..2)

local function getSessBoxClipButton(idx) -- idx expected 0..26
  local p = root.children.pager1
  local page = p and p.children.MAIN
  local grp  = page and page.children.SessBoxClip
  return grp and grp.children["Clip" .. tostring(idx)]
end

local function getClipNameLabel(idx) -- idx expected 0..26
  local p = root.children.pager1
  local page = p and p.children.MAIN
  local grp  = page and page.children.ClipNameLabel1
  return grp and grp.children["ClipName" .. tostring(idx)]
end

local function clearClipNames_all()
  for i = 0, 26 do
    local L = getClipNameLabel(i)
    if L then L.values.text = "" end
  end
end

local function clearSessBoxClipButtonsToNeutral()
  for i = 0, 26 do
    local btn = getSessBoxClipButton(i)
    if btn then setColorFromTable(btn, NEUTRAL_IDX) end
  end
end

-- ===== MIDI Handler =======
function onReceiveMIDI(msg)
    -- SONG KEY IN: ch2 CC41
  if msg and msg[1] == CC41_CH2 and msg[2] == CC41_NUM then
    local v = msg[3] or 0
    local idx0 = ccValueToSongKeyIndex0(v)           -- 0..16
    local keyName = SONG_KEYS[idx0 + 1] or "?"       -- "C".."B"

    -- Update radio selector (optional, keeps UI in sync)
    local sel = getSongKeySelector()
    if sel then
      songKeyUpdatingFromMidi = true
      sel.values.x = idx0
      songKeyUpdatingFromMidi = false
    end

    -- Update label text: pager1.MAIN.SongKeyLabel
    local lbl = getSongKeyLabel()
    if lbl then
      lbl.values.text = keyName
    end

    return
  end

  -- Your existing SysEx-only early guard
  if not (msg and msg[1] == 240 and msg[#msg] == 247) then return end

  -- A) COLORS on 126,1  ...............................................
  if msg[2] == 126 and msg[3] == 1 then
    local payload_len = (#msg - 4)
    if payload_len >= 1 and payload_len <= 9 then
      for i = 0, payload_len - 1 do
        local idx = tonumber(msg[4 + i]) or NEUTRAL_IDX
        if idx < 0 then idx = 0 elseif idx > 69 then idx = 69 end
        local fader = getFader(i)
        if fader then setColorFromTable(fader, idx) end
      end
      return
    end
    if payload_len >= 3 then
      local loop_number = msg[4]
      local idx = tonumber(msg[5]) or NEUTRAL_IDX
      if idx < 0 then idx = 0 elseif idx > 69 then idx = 69 end
      if #msg >= 7 and msg[6] ~= nil then
        local new_off = tonumber(msg[6])
        if new_off and new_off ~= CURRENT_OFFSET then CURRENT_OFFSET = new_off end
      end
      local zcol0 = map_to_window(loop_number)
      if zcol0 then
        local fader = getFader(zcol0)
        if fader then setColorFromTable(fader, idx) end
      end
      return
    end
    return
  end

  -- B) TRACK NAMES on 126,2 ...........................................
  if msg[2] == 126 and msg[3] == 2 then
    if #msg < 5 then return end
    local names = parse_names_from_bytes(msg, 4, #msg - 1)
    clearTrackNames_0_7()
    for i = 0, 7 do
      local L = getTrackNameLabel(i)
      if L then L.values.text = names[i + 1] or "" end
    end
    return
  end

  -- C) SET CONTROL on 126,3 ...........................................
  if msg[2] == 126 and msg[3] == 3 then
    local label_id = msg[4] or 1
    local text = ""
    for i = 5, #msg - 1 do text = text .. string.char(msg[i]) end
    local children = root.children.pager1.children.MAIN.children.ControlPager.children.Control.children.SetControlLabel.children
    if label_id >= 1 and label_id <= 16 then
      local target = children["label" .. label_id]
      if target then target.values.text = text end
    end
    return
  end

  -- D) CLIP NAMES on 126,4 ............................................
  if msg[2] == 126 and msg[3] == 4 then
    if #msg < 6 then return end
    local row = tonumber(msg[4]) or 0
    if row < 0 or row > 2 then
      print("csslog: Invalid clip names row in sysex, using 0")
      row = 0
    end
    local names = parse_names_from_bytes(msg, 5, #msg - 1)

    -- Map incoming 8 NUL-separated clip names into the 3-row layout (zero-based):
    -- row 0 -> ClipName0..ClipName7   (scene name is ClipName8)
    -- row 1 -> ClipName9..ClipName16  (scene name is ClipName17)
    -- row 2 -> ClipName18..ClipName25 (scene name is ClipName26)
    local base_map = {0, 9, 18}
    local base = base_map[row + 1]

    -- write up to 8 names into base..base+7
    for i = 0, 7 do
      local idx = base + i
      local L = getClipNameLabel(idx)
      if L then L.values.text = names[i + 1] or "" end
    end

    return
  end

  -- E) SCENE NAME on 126,5 ............................................
  if msg[2] == 126 and msg[3] == 5 then
    -- Expect: F0 7E 05 <row(0..2)> <ascii bytes...> F7
    if #msg < 5 then return end

    local row = tonumber(msg[4]) or 0
    if row < 0 or row > 2 then
      print("csslog: Invalid scene row in sysex, using 0")
      row = 0
    end

    local sname = ""
    for i = 5, #msg - 1 do sname = sname .. string.char(msg[i]) end

    -- Map incoming scene names to ClipName8, ClipName17, ClipName26 (zero-based)
    local scene_map = {8, 17, 26}
    local idx = scene_map[row + 1]
    local L = getClipNameLabel(idx)
    if L then L.values.text = sname end

    SCENE_ROW_PTR = (SCENE_ROW_PTR + 1) % 3
    return
  end

  -- F) TEMPO TEXT on 126,6 ............................................
  if msg[2] == 126 and msg[3] == 6 then
    if #msg < 5 then return end
    local tempo_text = ""
    for i = 4, #msg - 1 do tempo_text = tempo_text .. string.char(msg[i]) end
    local lbl = getTempoLabel()
    if lbl then lbl.values.text = tempo_text else print("TempoLabel not found in pager1 → MAIN") end
    return
  end

  -- K) SELECTED TRACK on 123,6 .....................................
  -- Expect: [240, 123, 6, <ascii bytes...>, 247]
  if msg[2] == 123 and msg[3] == 6 then
    if #msg < 5 then return end
    local track_name = ""
    for i = 4, #msg - 1 do track_name = track_name .. string.char(msg[i]) end
    local lblt = getSelectedTrackLabel()
    if lblt then
      lblt.values.text = track_name
    else
      print("SelectedTrack label not found in pager1 → MAIN")
    end
    return
  end

  -- L) SELECTED DEVICE on 123,7 .....................................
  if msg[2] == 123 and msg[3] == 7 then
    if #msg < 5 then return end
    local dev_name = ""
    for i = 4, #msg - 1 do dev_name = dev_name .. string.char(msg[i]) end
    local lbl = getSelectedDeviceLabel()
    if lbl then
      lbl.values.text = dev_name
    else
      print("SelectedDevice label not found in pager1 → MAIN")
    end
    return
  end

  -- J) NUMERATOR on 123,8 ..........................................
  -- Expect: [240, 126, 10, <numerator_byte>, 247]
  if msg[2] == 123 and msg[3] == 8 then
    if #msg < 5 then return end
    local num_text = ""
    for i = 4, #msg - 1 do num_text = num_text .. string.char(msg[i]) end
    local lbl = getNumeratorLabel()
    if lbl then
      lbl.values.text = num_text
    else
      print("Numerator label not found in pager1 → MAIN")
    end
    return
  end

  -- K) DENOMINATOR on 123,9 .........................................
  -- Expect: [240, 123, 9, <denominator_byte>, 247]
  if msg[2] == 123 and msg[3] == 9 then
    if #msg < 5 then return end
    local den_text = ""
    for i = 4, #msg - 1 do den_text = den_text .. string.char(msg[i]) end
    local lbl = getDenominatorLabel()
    if lbl then
      lbl.values.text = den_text
    else
      print("Denominator label not found in pager1 → MAIN")
    end
    return
  end

  -- M) DEVICE PARAMETER VALUES on 123,4 ...............................
  -- Expect: [240, 123, 4, <param_number(1..16)>, <ascii bytes...>, 247]
  if msg[2] == 123 and msg[3] == 4 then
    if #msg < 6 then return end
    local param_num = tonumber(msg[4]) or 0
    if param_num < 1 or param_num > 16 then return end

    local param_value = ""
    for i = 5, #msg - 1 do param_value = param_value .. string.char(msg[i]) end

    local lbl = getDeviceParameterValueLabel(param_num)
    if lbl then
      lbl.values.text = param_value
    else
      print("Device parameter value label " .. param_num .. " not found in pager1 → MAIN → ControlPager → Device → SelectedDeviceParameterNames")
    end
    return
  end

  -- M) DEVICE PARAMETER NAMES on 123,5 ................................
  -- Expect: [240, 123, 5, <param_number(1..16)>, <ascii bytes...>, 247]
  if msg[2] == 123 and msg[3] == 5 then
    if #msg < 6 then return end
    local param_num = tonumber(msg[4]) or 0
    if param_num < 0 or param_num > 16 then return end
    
    local param_name = ""
    for i = 5, #msg - 1 do param_name = param_name .. string.char(msg[i]) end
    
    local lbl = getDeviceParameterNameLabel(param_num)
    if lbl then
      lbl.values.text = param_name
    else
      print("Device parameter name label " .. param_num .. " not found in pager1 → MAIN → ControlPager → Device → SelectedDeviceParameterNames")
    end
    return
  end

  -- G) CLIP BUTTON COLORS on 126,7 ....................................
  if msg[2] == 126 and msg[3] == 7 then
    local payload_len = (#msg - 5)

    -- Reset token (single 127) clears all session buttons
    if payload_len == 1 and msg[5] == 127 then
      CLIP_COLOR_PTR = 0
      clearSessBoxClipButtonsToNeutral()
      return
    end

    if payload_len >= 1 and payload_len <= 8 then
      local row = tonumber(msg[4]) or 0
      if row < 0 or row > 2 then
        print("csslog: Invalid clip colors row in sysex, using 0")
        row = 0
      end

      -- Map incoming up-to-8 color bytes into the corresponding row of Clip buttons (zero-based).
      -- row 0 -> Clip0..Clip7  (scene button is Clip8)
      -- row 1 -> Clip9..Clip16 (scene button is Clip17)
      -- row 2 -> Clip18..Clip25 (scene button is Clip26)
      local base_map = {0, 9, 18}
      local base = base_map[row + 1]

      for i = 0, payload_len - 1 do
        local idx = tonumber(msg[5 + i]) or NEUTRAL_IDX
        if idx < 0 then idx = 0 elseif idx > 69 then idx = 69 end
        local btn = getSessBoxClipButton(base + i)
        if btn then setColorFromTable(btn, idx) end
      end
    end
    return
  end

  -- H) SCENE BUTTON COLOR on 126,8 (when exactly 6 bytes) ................
  if msg[2] == 126 and msg[3] == 8 and #msg == 6 then
    local row = tonumber(msg[4]) or 0
    if row < 0 or row > 2 then
      print("csslog: Invalid scene color row in sysex, using 0")
      row = 0
    end
    
    local color_idx = tonumber(msg[5]) or NEUTRAL_IDX
    if color_idx < 0 then color_idx = 0 elseif color_idx > 69 then color_idx = 69 end
    
    -- Map scene buttons: row 0 -> Clip8, row 1 -> Clip17, row 2 -> Clip26
    local scene_button_map = {8, 17, 26}
    local scene_btn_idx = scene_button_map[row + 1]
    local btn = getSessBoxClipButton(scene_btn_idx)
    if btn then setColorFromTable(btn, color_idx) end
    
    return
  end

  -- I) CHAIN NAMES on 125,1..8 (Tracks 1-8) ...........................
  if msg[2] == 125 and msg[3] >= 1 and msg[3] <= 8 then
    -- Note: The `clearChainLabels()` call for msg[3]==1 is preserved, but the function itself is not defined in this script.
    if msg[3] == 1 and #msg == 5 and msg[4] == 255 then clearChainLabels(); return end
    if #msg < 6 then return end

    local chain_number = msg[4]
    local chain_name = ""
    for i = 5, #msg - 1 do chain_name = chain_name .. string.char(msg[i]) end

    if chain_number >= 0 and chain_number <= 19 then
      local pager = root.children.pager1
      local page = pager and pager.children.PATCHES
      
      local section_map = {
        [1] = "SECTION1A", [2] = "SECTION1B",
        [3] = "SECTION2A", [4] = "SECTION2B",
        [5] = "SECTION3A", [6] = "SECTION3B",
        [7] = "SECTION4A", [8] = "SECTION4B"
      }
      local section_name = section_map[msg[3]]

      if section_name then
        local section = page and page.children[section_name]
        local group = section and section.children.ChainLabel
        local target_label = group and group.children[tostring(chain_number)]

        if target_label then 
          target_label.values.text = chain_name 
        end
      end
    end
    return
  end

  -- I) PARAMETER NAMES on 125,8 (when longer than 6 bytes) .............
  -- Expect: [240, 125, 8, parameter_number(1..16), <ascii bytes...>, 247]
  if msg[2] == 125 and msg[3] == 8 and #msg > 6 then
    if #msg < 7 then return end
    local pnum = tonumber(msg[4]) or 1            -- treat incoming numbers as 1-based
    if pnum < 1 or pnum > 16 then return end      -- only accept 1..16
    local pname = ""
    for i = 5, #msg - 1 do pname = pname .. string.char(msg[i]) end

    local pager = root.children.pager1
    local page  = pager and pager.children.SYNTHS
    local group = page and page.children.BlueHandText
    if group then
      local label = group.children[tostring(pnum)]
      if label then label.values.text = pname end
    end
    return
  end

end
