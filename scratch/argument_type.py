import json
from opcodes import Primitives


# Yoinked from
# https://github.com/scratchfoundation/scratch-vm/blob/e5950c3de5adb4859befc6fe1b19a2142be5c192/src/serialization/sb3.js



PRIMITIVE_OPCODE_INFO_MAP = {
    "math_number": [Primitives.MATH_NUM, "NUM"],
    "math_positive_number": [Primitives.POSITIVE_NUM, "NUM"],
    "math_whole_number": [Primitives.WHOLE_NUM, "NUM"],
    "math_integer": [Primitives.INTEGER_NUM, "NUM"],
    "math_angle": [Primitives.ANGLE_NUM, "NUM"],

     # I realise that this uses both UK and US spelling, but the Scratch VM uses both internally, 
     # so I'm forced to follow with their terribleness. 
    "colour_picker": [Primitives.COLOR_PICKER, "COLOUR"],
    "text": [Primitives.TEXT, "TEXT"],
    "event_broadcast_menu": [Primitives.BROADCAST, "BROADCAST_OPTION"],
    "data_variable": [Primitives.VAR, "VARIABLE"],
    "data_listcontents": [Primitives.LIST, "LIST"]
}



"""
A field is a text-box or a drop down menu, etc. 
They are embedded wtihin blocks. Some have the ability to have reporters dropped into it. 
    In this case, no such field exists, but an input does, which is the shadow block. 
"""

"""
A reporter block is one of the blocks in scratch that is typically used as an input. 
Operator blocks are such a reporter block. 
"""


"""
A shadow block is a reporter in an input for which one can enter or pick a value, 
and which cannnot be dragged around but can be replaced by a normal reporter.

See: OPCODES["Menus"]

Scratch internally considers these to be blocks although they are not usually 
thought of as such. 
(These notions come from Blockly, which Scratch Blocks is based on.) 
"""


"""
Potential 'inputs' property format:

1 = Input is a shadow
2 = There is no shadow
3 = There is a shadow, but obscured by input. 

0th index 1-3
1st index ID of input or array of input. 
2nd index is ID of input or array of input <-- only if 0th index is 3. 
"""

OptionalInt = int | None
OptionalStr = str | None
OptionalList = list | None
OptionalDict = dict | None


class BlockBase:
    ID = 0

    def __init__(self, opcode: str, next_: OptionalStr=None, parent: OptionalStr=None, inputs: OptionalDict=None, fields: OptionalDict=None, shadow: bool=False, toplevel: bool=False, x: OptionalInt=None, y: OptionalInt=None):
        self.opcode = opcode
        self.next = next_
        self.parent = parent
        self.inputs = inputs or {}
        self.fields = inputs or {}
        self.shadow = shadow
        self.toplevel = toplevel
        self.x = x
        self.y = y
        self.ID = str(BlockBase.ID + 1)
        BlockBase.ID += 1


class Mutation(BlockBase): 
    def __init__(self, opcode, proccode, next_ = None, parent = None, inputs = None, fields = None, shadow = False, toplevel = False, x = None, y = None, 
                 children: OptionalList=None, argumentids: OptionalList=None, argumentnames: OptionalList=None, warp: bool=False):
        super().__init__(opcode, next_, parent, inputs, fields, shadow, toplevel, x, y)
        self.mutation = {
            "tagName": "mutation",
            "children": children or [],
            "proccode": proccode,
            "argumentids": argumentids or [],
            "argumentnames": argumentnames or [],
            "warp": warp

        }


class Reporter:
    def __init__(self):
        pass


class Block:
    def __init__(self, opcode: str, ):
        pass


def serialise_block(block: BlockBase):
    data: dict[str, int | list | str] = {
        "opcode": block.opcode,
        "next": block.next,
        "parent": block.parent,
        "inputs": block.inputs,
        "fields": block.fields,
        "shadow": block.shadow,
        "toplevel": block.toplevel,
    }

    if block.toplevel is True:
        data["x"] = block.x
        data["y"] = block.y

    if type(block) is Mutation:
        data["mutation"] = block.mutation
    
    return json.dumps(data)


def serialise_blocks(blocks: list[BlockBase]):
    serialised = {}
    for block in blocks:
        serialised[block.ID] = serialise_block(block)
    return serialised
