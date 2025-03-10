from enum import Enum
from argument_type import BlockBase, serialise_block, serialise_blocks
# Many thanks!
# https://en.scratch-wiki.info/wiki/List_of_Block_Opcodes


class Primitives(Enum):
    INPUT_SAME_BLOCK_SHADOW = 1
    INPUT_BLOCK_NO_SHADOW = 2 
    INPUT_DIFF_BLOCK_SHADOW = 3
    MATH_NUM = 4 # Yes, my soul also dies because they used 'Math' instead of 'Maths'
    POSITIVE_NUM = 5
    WHOLE_NUM = 6
    INTEGER_NUM = 7
    ANGLE_NUM = 8
    COLOR_PICKER = 9
    TEXT = 10
    BROADCAST = 11
    VAR = 12
    LIST = 13


MOTION = {
    "move": "motion_movesteps",
    "turn_right": "motion_turnright",
    "turn_left": "motion_turnleft",
    "goto": "motion_goto",
    "goto_x_y": "motion_gotoxy",
    "glide_to": "motion_glideto",
    "glide_to_x_y": "motion_glidesecdstoxy",
    "point_dir": "motion_pointindirection",
    "point_to": "motion_pointtowards",
    "change_x": "motion_changexby",
    "set_x": "motion_setx",
    "change_y": "motion_changeyby",
    "set_y": "motion_sety",
    "bounce_on_edge": "motion_ifonedgebounce",
    "set_rotation_style": "motion_setrotationstyle",
    "x": "motion_xposition",
    "y": "motion_ypostition" 
}


LOOKS = {
    "say_for": "looks_sayforsecs",
    "say": "looks_say",
    "think_for": "looks_thinkforsecds",
    "think": "looks_think",
    "switch_costume_to": "looks_switchcostumeto",
    "next_costume": "looks_nextcostume",
    "switch_backdrop_to": "looks_switchbackdropto",
    "switch_backdrop_to_and_wait": "looks_switchbackdroptoandwait",
    "next_backdrop": "looks_nextbackdrop",
    "change_size_by": "looks_changesizeby",
    "set_size": "looks_setsizeto",
    "change_effect_by": "looks_changeeffectby",
    "set_effect": "looks_seteffectto",
    "clear_effects": "looks_cleargraphiceffects",
    "show": "looks_show",
    "hide": "looks_hide",
    "go_to_layer": "looks_gotofrontback",
    "change_layer_by": "looks_goforwardbackwardlayers",
    "costume_number": "looks_costumenumbername",
    "backdrop_number": "looks_backdropnumbername",
    "size": "looks_size"
}


SOUND = {
    "play_sound_until_done": "sound_playuntildone",
    "play_sound": "sound_play",
    "stop_all_sounds": "sound_stopallsounds",
    "change_sound_effect_by": "sound_changeeffectby",
    "set_sound_effect": "sound_seteffectto",
    "clear_sound_effects": "sound_cleareffects",
    "change_volume_by": "sound_changevolumeby",
    "set_volume": "sound_setvolumeto",
    "volume": "sound_volume"
}


EVENT = {
    "when_flag_clicked": "event_whenflagclicked",
    "when_key_pressed": "event_whenkeypressed",
    "when_sprite_clicked": "event_whenthisspriteclicked",
    "when_stage_clicked": "event_whenstageclicked",
    "when_backdrop_switched_to": "event_whenbackdropswitchesto",
    "when_greater_than": "event_whengreaterthan",
    "when_broadcast_received": "event_whenbroadcastreceived",
    "broadcast_message": "event_broadcast",
    "broadcast_message_and_wait": "event_broadcastandwait"
}


CONTROL = {
    "wait_for": "control_wait",
    "repeat": "control_repeat",
    "forever": "control_forever",
    "if": "control_if",
    "if_else": "control_if_else",
    "wait_until": "control_wait_until",
    "repeat_until": "control_repeat_until",
    "stop": "control_stop",
    "when_start_as_clone": "control_start_as_clone",
    "clone": "control_create_clone_of",
    "delete_this_clone": "control_delete_this_clone" 
}


SENSING = {
    "is_touching_object": "sensing_touchingobject",
    "is_touching_colour": "sensing_touching_color",
    "is_colour_touching_colour": "sensing_coloristouchingcolor",
    "distance_to": "sensing_distanceto",
    "ask_and_wait": "sensing_askandwait",
    "answer": "sensing_answer",
    "is_key_pressed": "sensing_keypressed",
    "is_mouse_down": "sensing_mousedown",
    "mouse_x": "sensing_mousex",
    "mouse_y": "sensing_mousey",
    "set_drag_mode": "sensing_setdragmode",
    "loudness": "sensing_loudness",
    "timer": "sensing_timer",
    "reset_timer": "sensing_resettimer",
    "get_value_of": "sensing_of",
    "get_current_time": "sensing_current",
    "days_since_2000": "sensing_dayssince2000",
    "username": "sensing_username"
}


OPERATOR = {
    "add": "operator_add",
    "sub": "operator_subtract",
    "mul": "operator_multiply",
    "div": "operator_divide",
    "random": "operator_random",
    "gt": "operator_gt",
    "ls": "operator_lt",
    "equals": "operator_equals",
    "and": "operator_and",
    "or": "operator_or",
    "not": "operator_not",
    "join": "operator_join",
    "get_letter_of": "operator_get_letter_of",
    "length": "operator_length",
    "contains": "operator_contains",
    "modulo": "operator_modulo",
    "round": "operator_round",
    "maths_op": "operator_mathop"
}


VARIABLE = {
    "variable": "data_variable",
    "set_variable": "data_setvariableto",
    "change_variable": "data_changevariableby",
    "show_variable": "data_showvariable",
    "hide_variable": "data_hidevariable",
}


LIST = {
    # lists
    "list_contents": "data_listcontents",
    "append": "data_addtolist",
    "remove": "data_deleteoflist",
    "clear": "data_deletealloflist",
    "insert": "data_insertatlist",
    "replace": "data_replaceitemoflist",
    "get_item": "dataitemoflist",
    "get_index": "data_itemnumoflist",
    "length_of_list": "data_lengthoflist",
    "in": "data_listcontainsitem",
    "show_list": "data_showlist",
    "hide_list": "data_hidelist"
}


MY_BLOCKS = {
    "define": "procedures_definition",
    "call": "procedures_call",
    "string_number": "argument_reporter_string_number",
    "boolean": "argument_reporter_boolean"
}


MENUS = {
    "go_to_menu": "motion_goto_menu",
    "glide_to_menu": "motion_glideto_menu",
    "point_towards_menu": "motion_pointtowards_menu",
    "rotation_style_menu": "motion_setrotationstyle",
    "costume_menu": "looks_costume",
    "backdrop_menu": "looks_backdrops",
    "sounds_menu": "sounds_sounds_menu",
    "broadcast_menu": "event_broadcast_menu",
    "clone_menu": "control_create_clone_of_menu",
    "touching_menu": "sensing_touchingobject_menu",
    "distance_menu": "sensing_distancetomenu",
    "key_menu": "sensing_keyoptions",
    "object_menu": "sensing_of_object_menu"
}


OPCODES = {
    "Motion": MOTION,
    "Looks": LOOKS,
    "Sound": SOUND,
    "Event": EVENT,
    "Control": CONTROL,
    "Sensing": SENSING,
    "Operator": OPERATOR,
    "List": LIST,
    "Variable": VARIABLE,
    "MyBlocks": MY_BLOCKS,
    "Menus": MENUS
}


INPUTS = {
    "operator_random": {"FROM": [
        Primitives.INPUT_SAME_BLOCK_SHADOW,
        [
            Primitives.MATH_NUM,
            "1"
        ]
    ],
    "TO": [ # <-- fuck you scratch, why can't you use "NUM1" and "NUM2" everywhere?
        Primitives.INPUT_SAME_BLOCK_SHADOW,
        [
            Primitives.MATH_NUM,
            "10"
        ]
    ]},
    "operator_add": {
        "NUM1": [
            Primitives.INPUT_SAME_BLOCK_SHADOW,
            [
                Primitives.MATH_NUM,
                ""
            ]
        ],
        "NUM2": [
            Primitives.INPUT_SAME_BLOCK_SHADOW,
            [
                Primitives.MATH_NUM,
                ""
            ]
        ]
    }
}


if __name__ == "__main__":
    goto_menu = BlockBase(MENUS["go_to_menu"],
                        fields={
                            "TO": [
                                "_random_",
                                None
                            ]
                        })


    point_menu = BlockBase(MENUS["point_towards_menu"], 
                        fields={
                            "TOWARDS": [
                                "_mouse_",
                                None
                            ]
                        })

    style_menu = BlockBase(MENUS["rotation_style_menu"],
                        fields={
                            "STYLE": [
                                "left-right",
                                None
                            ]
                        })