from _Framework.EncoderElement import EncoderElement
class CMDEncoderElement(EncoderElement):

    def __init__(self, msg_type, channel, identifier, map_mode, sensitivity):
        EncoderElement.__init__(self, msg_type, channel, identifier, map_mode, sensitivity)
        self._mapping_sensitivity = 7
        self.set_needs_takeover(False)
        self.set_report_values(False, False)
    def _mapping_feedback_values(self):
        value_map = tuple(range(32,48))
        if self._mapping_feedback_delay != 0:
            if self._msg_type != MIDI_PB_TYPE:
                value_map = tuple(range(16))
            else:
                value_pairs = []
                for value in xrange(16384):
                    value_pairs.append((value >> 8 & 16, value & 16))

                value_map = tuple(value_pairs)
        return value_map
    