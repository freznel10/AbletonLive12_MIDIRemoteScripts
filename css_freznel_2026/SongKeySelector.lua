----- MIDI messages to be sent -------------------------

local a = {}  -- our array to store the messages packed as lists
  -- radiobuttons start index at 0 (0..16)
  -- send CONTROLCHANGE on MIDI channel 2: use MIDIMessageType.CONTROLCHANGE + 1
  -- CC number used for song key is 41
  -- we send the midpoint value for each key-range (C..B) as observed
-- Midpoint values for ranges: C..B (indices 0..16)
local SONG_KEY_MIDPOINTS = {
  2,   -- C   (0-3)
  7,   -- C#  (4-9)
 15,   -- Db  (10-19)
 24,   -- D   (20-27)
 31,   -- D#  (28-34)
 40,   -- Eb  (36-43)
 48,   -- E   (44-51)
 56,   -- F   (52-59)
 64,   -- F#  (60-67)
 72,   -- Gb  (68-75)
 80,   -- G   (76-83)
 88,   -- G#  (84-91)
 96,   -- Ab  (92-99)
104,   -- A   (100-107)
112,   -- A#  (108-115)
120,   -- Bb  (116-123)
126,   -- B   (124-127)
}

for i = 0, 16 do
  local idx = i + 1 -- Lua table index
  local val = SONG_KEY_MIDPOINTS[idx]
  a[i] = { MIDIMessageType.CONTROLCHANGE + 1, 41, val }
end

----- MIDI connections to use --------------------------
 
                --   1      2      3      4      5 
MIDIconnections = { true, false, false, false, false }

--------------------------------------------------------

----- OSC messages to be sent --------------------------

local b = {}  -- our array to store the messages packed as lists
        -- create matching OSC messages for the 17 radio steps (0..16)
        -- OSC path chosen here: /1/songkey (adjust in TouchOSC if needed)
        -- values are normalized midpoints (midpoint / 127)
local SONG_KEY_OSC = {
  0.016, -- 2/127
  0.055, -- 7/127
  0.118, -- 15/127
  0.189, -- 24/127
  0.244, -- 31/127
  0.315, -- 40/127
  0.378, -- 48/127
  0.441, -- 56/127
  0.504, -- 64/127
  0.567, -- 72/127
  0.630, -- 80/127
  0.693, -- 88/127
  0.756, -- 96/127
  0.819, -- 104/127
  0.882, -- 112/127
  0.945, -- 120/127
  0.992, -- 126/127
}

for i = 0, 16 do
  local idx = i + 1
  b[i] = { '/1/songkey', SONG_KEY_OSC[idx] }
end


function onValueChanged(key)
  if songKeyUpdatingFromMidi then return end
  if (key == "x") then        -- when the button changes
  
    -- send MIDI , MIDIconnections is optional
    sendMIDI( a[self.values.x] )   

  end
end