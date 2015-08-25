"""
Define the rooms in the world.

A dictionary of all the rooms to randomly select from.
Each entry takes the form:
ROOM_NAME: [PrimaryPlayerMotion, *room_layout]


PrimaryPlayerMotion is a variable that tells the game what direction
the player is moving in through the room.

StartingRoom and EndingRoom must exist somewhere
   KEY for room_array:
       S is stone
       P is spike
       B is a breakable wall
       R is a turret
       T is a block that stops the timer
       W is a weapon chest
       D is door <- IMPORTANT, you need a door at the top and bottom to make the logic work
"""

import constants as c

room_dict = {
    "StartingRoom":
        [c.MOVE_RIGHT,
        "SSSSSSSS",
        "S      S",
        "S      S",
        "SSSSSDDS"
        ],

    "TransitionRoom":
        [c.MOVE_DOWN,
         "SDDS",
         "S  S",
         "S  S",
         "S  S",
         "S  S",
         "SDDS"
        ],

    "EndingRoom":
        [c.MOVE_DOWN,
        "SSSDDSSS",
        "S      S",
        "S      S",
        "S      S",
        "SP    PS",
        "SRRRRRRS"
        ],

    "Room01":
        [c.MOVE_DOWN,
        "SSDDSS",
        "SF   S",
        "S    S",
        "SS   S",
        "S    S",
        "S   SS",
        "S    S",
        "S S SS",
        "S    S",
        "S    S",
        "SSDDSS"
        ],

    "Room02":
        [c.MOVE_LEFT,
        "SSSSSSSSSDDS",
        "S          S",
        "SP     PS PS",
        "SSDDSSSSSSSS"
        ],

    "Room03":
        [c.MOVE_RIGHT,
        "SSDDSSSSSSSS",
        "S          S",
        "S     B P  S",
        "SSSSSSSSSDDS"
        ],

    "Room04":
        [c.MOVE_RIGHT,
        "SSDDSSSSSSSSSSSSS",
        "S               S",
        "SV              S",
        "S     SSSSSSS   S",
        "S      S   S    S",
        "S    S V S      S",
        "SSSSSSSSSSSSSDDSS"
        ],

    "Room05":
        [c.MOVE_LEFT,
        "SSSSSSSSSSSSSSSSDDS",
        "S                 S",
        "S                 S",
        "S                 S",
        "S    SSSSSSSSP  SSS",
        "S    S   S   SS   S",
        "S  B   B   B      S",
        "SDDSSSSSSSSSSSSSSSS"
        ],

    "Room06":
        [c.MOVE_RIGHT,
        "SSDDSSSSSSSS",
        "S          S",
        "S      B   S",
        "S  G  BB   S",
        "SSSSSSSSDDSS"
        ],

    "Room07":
        [c.MOVE_DOWN,
        "SSDDSS",
        "S    S",
        "S    S",
        "S    S",
        "S    S",
        "SV  VS",
        "S    S",
        "S BBBS",
        "S    S",
        "SBBB S",
        "S    S",
        "S    S",
        "SSDDSS"
        ],

    "Room08":
        [c.MOVE_LEFT,
        "SSSSSSSSSSSDDSSS",
        "S       V      S",
        "S   B          S",
        "SS  BB         S",
        "SSDDSSSSSSSSSSSS"
        ],

    "Room09":
        [c.MOVE_RIGHT,
        "SSDDSSSSSSSS",
        "SV  V      S",
        "S          S",
        "SSSSSSDDSSSS"
        ],

    "Room10":
        [c.MOVE_RIGHT,
        "SSSSDDSSSSSSSS",
        "S  B        VS",
        "S  B      B  S",
        "S PP   G BB  S",
        "SSSSSSSSSSSDDS"
        ],

    "Room11":
        [c.MOVE_RIGHT,
        "SSDDSSSSSSSS",
        "SF         S",
        "SP   PP    S",
        "SSSSSSSSDDSS"
        ]
}