{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "Hi!",
            "Expected": "Hello!",
            "Tree": "proper_q(x4,named(Hawaii,x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "5a55771f-2f05-4c41-b73e-b65a85145b1b"
        },
        {
            "Command": "Hello!",
            "Expected": "Hello!",
            "Tree": "proper_q(x4,named(Hawaii,x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "b00d2816-95d2-4e45-8340-636658ee6264"
        },
        {
            "Command": "alright, could we have a table?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_all+right_a_1(i4,_a_q(x14,_table_n_1(x14),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _have_v_1_able(e2,x3,x14)])))",
            "Enabled": true,
            "ID": "c1b2d49d-7d2e-4003-9dea-d43f04a6a3a8"
        },
        {
            "Command": "ok, can we have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "_okay_a_1(i4,_a_q(x14,_menu_n_1(x14),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _have_v_1_able(e2,x3,x14)])))",
            "Enabled": true,
            "ID": "cf3d3f38-e5fc-47a2-adac-8f11cd307446"
        },
        {
            "Command": "well, can we have a table?",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "_well_a_1(i4,_a_q(x14,_table_n_1(x14),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _have_v_1_able(e2,x3,x14)])))",
            "Enabled": true,
            "ID": "0015b724-bede-48ff-87ce-6b4b7df82564"
        },
        {
            "Command": "a table for two for now",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "def_implicit_q(x10,basic_numbered_hour(2,x10),def_implicit_q(x17,[time_n(x17), _now_a_1(e22,x17)],_a_q(x4,[_table_n_1(x4), _for_p(e16,x4,x17), _for_p(e9,x4,x10)],unknown(e2,x4))))",
            "Enabled": true,
            "ID": "e9c478c5-5424-4505-a447-9a8d86045592"
        },
        {
            "Command": "just menus for now",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "def_implicit_q(x12,[time_n(x12), _now_a_1(e17,x12)],[udef_q(x4,[_menu_n_1(x4), _for_p(e11,x4,x12)],unknown(e2,x4)), _just_x_deg(e6,u7)])",
            "Enabled": true,
            "ID": "74a5910c-a37b-40e7-93e1-91f5f7e1adbe"
        },
        {
            "Command": "No for now",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a menu for you.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x10,[time_n(x10), _now_a_1(e15,x10)],_no_a_1(i7,[_for_p(e9,e2,x10), unknown(e2,u5)]))",
            "Enabled": true,
            "ID": "be5c1696-486a-442f-835e-40e10fdd6641"
        },
        {
            "Command": "OK",
            "Expected": "\nWaiter: What can I get you?",
            "Tree": "_okay_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "5820f7bb-5471-4621-b015-2395b08a1cf7"
        },
        {
            "Command": "perfect",
            "Expected": "\nWaiter: What can I get you?",
            "Tree": "[_perfect_a_1(e5,u4), unknown(e2,u4)]",
            "Enabled": true,
            "ID": "0ec0db9a-43f5-4e32-b381-51246200830a"
        }
    ],
    "ElapsedTime": 7.68568
}