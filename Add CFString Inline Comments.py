# Go through CFString section, and add inline comments to any uses of those strings with the contents of the string
# This is only really needed on ARM.  It seems to happen already on x64
# bradenthomas@me.com

import struct

# configuration parameters, adjust as needed:
ENDIANNESS = "<" # Little endian = <, Big endian = >

# helper methods
def read_data(segment, addr, dlen):
    if segment is None:
        segment = doc.getSegmentAtAddress(addr)
    return "".join(chr(segment.readByte(addr+x)) for x in range(0,dlen))

# first, find the CFString segment
doc = Document.getCurrentDocument()
cfstring_seg = None
for seg_idx in range(0,doc.getSegmentCount()):
    cur_seg = doc.getSegment(seg_idx)
    if cur_seg.getName() == "__cfstring":
        cfstring_seg = cur_seg
        cfstring_range = cur_seg
        break
    elif cur_seg.getName() == "__DATA":
        for section in cur_seg.getSectionsList():
            if section.getName() == "__cfstring":
                cfstring_seg = cur_seg
                cfstring_range = section
                break
if not cfstring_seg:
    raise Exception("No CFString segment found")

# Run though CFStrings
ptr_size = 8 if doc.is64Bits() else 4
struct_typechar = "Q" if doc.is64Bits() else "I"
for addr in xrange(cfstring_range.getStartingAddress(), cfstring_range.getStartingAddress()+cfstring_range.getLength(), ptr_size*4):
    cstr_ptr, cstr_len = struct.unpack(ENDIANNESS + struct_typechar * 2, read_data(cfstring_seg, addr + ptr_size * 2, ptr_size * 2))

    for xref in cfstring_seg.getReferencesOfAddress(addr):
        xref_seg = doc.getSegmentAtAddress(xref)
        existing_inline_comment = xref_seg.getInlineCommentAtAddress(xref)
        if existing_inline_comment is None or existing_inline_comment.startswith("0x"):
            cstr_data = str(read_data(None, cstr_ptr, cstr_len))
            doc.log("Set inline comment at 0x%x: %s"%(xref, repr(cstr_data)))
            xref_seg.setInlineCommentAtAddress(xref, "@" + repr(cstr_data))
