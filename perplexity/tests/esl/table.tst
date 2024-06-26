{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "Could we have a table for two, please?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,def_implicit_q(x17,basic_numbered_hour(2,x17),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),[_please_a_1(e23,e10), event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "8a5eb15d-aec5-4844-9e37-8c9058e8e392"
        },
        {
            "Command": "I need a table for 2",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_need_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a3857ac3-6002-477d-8e28-dcbed11f60e6"
        },
        {
            "Command": "table for two, please",
            "Expected": "WRONG NEEDS NEW GRAMMAR: I don't know the way you used: for",
            "Tree": "None",
            "Enabled": true,
            "ID": "ef997ec5-4d75-4d77-ac29-d63d475bfa5d"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "293837ea-30f7-4bcf-8093-3a1ce8ac9453"
        },
        {
            "Command": "I want a water and a table",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a water when you have a table.\nHost: How many in your party?",
            "Tree": "_a_q(x13,_water_n_1(x13),_a_q(x18,_table_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "321e3d3c-653d-4393-85e3-2542de6db1af"
        },
        {
            "Command": "I want a table and a menu",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How many in your party?",
            "Tree": "_a_q(x13,_table_n_1(x13),_a_q(x18,_menu_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "24e9de01-d097-4916-ad77-7a7e5538dbe7"
        },
        {
            "Command": "I want a table and a steak",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a steak when you have a table.\nHost: How many in your party?",
            "Tree": "_a_q(x13,_table_n_1(x13),_a_q(x18,_steak_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "0631b2c0-2849-4806-b96c-dc961b14ea31"
        },
        {
            "Command": "Let's start with a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x10,_table_n_1(x10),pronoun_q(x5,pron(x5),[_with_p(e9,e2,x10), _start_v_1(e2,x5)]))",
            "Enabled": true,
            "ID": "5bf54692-5d9b-408c-8b19-bb6f986082e2"
        },
        {
            "Command": "Could I start with a table?",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x12,_table_n_1(x12),pronoun_q(x3,pron(x3),[_with_p(e11,e10,x12), event_replace(u99,e2,e10), _start_v_1_able(e2,x3)]))",
            "Enabled": true,
            "ID": "fe485f27-c4ce-46c7-ad85-d6a3a3f3ced8"
        },
        {
            "Command": "Can I start with a table?",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x12,_table_n_1(x12),pronoun_q(x3,pron(x3),[_with_p(e11,e10,x12), event_replace(u99,e2,e10), _start_v_1_able(e2,x3)]))",
            "Enabled": true,
            "ID": "c86ca27d-1d95-4bc4-be3b-2d322b4aab64"
        },
        {
            "Command": "Hi, table for 2",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "proper_q(x10,named(Hawaii,x10),number_q(x17,card(2,x17,i23),udef_q(x4,[_table_n_1(x4), _for_p(e16,x4,x17), compound(e9,x4,x10)],unknown(e2,x4))))",
            "Enabled": true,
            "ID": "6c18bda1-3844-4677-9fc9-8fb867b69429"
        },
        {
            "Command": "Hello, table for 2",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "proper_q(x10,named(Hawaii,x10),number_q(x17,card(2,x17,i23),udef_q(x4,[_table_n_1(x4), _for_p(e16,x4,x17), compound(e9,x4,x10)],unknown(e2,x4))))",
            "Enabled": true,
            "ID": "dbcc0867-b71d-4f35-948c-b05c4c6af90f"
        },
        {
            "Command": "Howdy, table for 2",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "proper_q(x10,named(Hawaii,x10),number_q(x17,card(2,x17,i23),udef_q(x4,[_table_n_1(x4), _for_p(e16,x4,x17), compound(e9,x4,x10)],unknown(e2,x4))))",
            "Enabled": true,
            "ID": "3840f232-880b-48de-ba47-f4cea768b7a4"
        },
        {
            "Command": "hello, table for 2, please",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "proper_q(x4,named(Hawaii,x4),number_q(x17,card(2,x17,i23),udef_q(x6,[_table_n_1(x6), _for_p(e16,x6,x17)],[_please_a_1(e24,e2), appos(e5,x4,x6), unknown(e2,x4)])))",
            "Enabled": true,
            "ID": "19f0bc45-2a55-4c94-b775-eca3afd7979c"
        },
        {
            "Command": "Howdy, could I have a table",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x16,_table_n_1(x16),[event_replace(u99,e8,e15), _have_v_1_able(e8,x3,x16)]))",
            "Enabled": true,
            "ID": "13882ec7-3e70-4025-96b7-e5e00b974eb2"
        },
        {
            "Command": "Hi, I want a table for 2, please?",
            "Expected": "I don't understand the way you are using: want",
            "Tree": "_a_q(x13,number_q(x19,card(2,x19,i25),[_table_n_1(x13), _for_p(e18,x13,x19)]),pronoun_q(x3,pron(x3),[_please_a_1(e26,e12), _want_v_1(e12,x3,x13)]))",
            "Enabled": true,
            "ID": "1fad1ba9-a1c9-43c8-af00-48b7b20cc0d7"
        },
        {
            "Command": "Hi, could I have a table for 2, please?",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x16,number_q(x22,card(2,x22,i28),[_table_n_1(x16), _for_p(e21,x16,x22)]),[_please_a_1(e29,e15), event_replace(u99,e8,e15), _have_v_1_able(e8,x3,x16)]))",
            "Enabled": true,
            "ID": "5a528908-6309-4d4d-b8e5-b945d5587d7e"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5f1b19be-b63b-4074-911a-00dc1847b94a"
        },
        {
            "Command": "Are there any tables?",
            "Expected": "Yes.",
            "Tree": "_any_q(x4,_table_n_1(x4),_be_v_there(e2,x4))",
            "Enabled": true,
            "ID": "a903e437-e680-4990-877b-7e8fa1079924"
        },
        {
            "Command": "Are any tables available?",
            "Expected": "Yes.",
            "Tree": "_any_q(x3,_table_n_1(x3),_available_a_to-for(e2,x3,u8))",
            "Enabled": true,
            "ID": "3aac6c9d-c6c1-4d4a-93f5-3d6350cdda9f"
        },
        {
            "Command": "I get a table?",
            "Expected": "I'm not sure what that means.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_get_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d3b37b3f-5323-4310-b004-fe8fb4e49208"
        },
        {
            "Command": "Do you have a table?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "46c5774e-2bce-4015-ac80-768a09a28d80"
        },
        {
            "Command": "I will have a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "51920fb5-d90b-419c-beee-483c9525d2a2"
        },
        {
            "Command": "I will sit down",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "9cf12d44-d1bb-4c9a-bde8-915f7f8e0747"
        },
        {
            "Command": "I would like to sit",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _sit_v_1_request(e2,x3)])",
            "Enabled": true,
            "ID": "e57230ed-8ed0-4367-ab6d-d3ee17138dc5"
        },
        {
            "Command": "I would love to sit",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _sit_v_1_request(e2,x3)])",
            "Enabled": true,
            "ID": "c2877e87-aaec-4dc5-8af5-e23d9581ecf3"
        },
        {
            "Command": "Can I sit?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _sit_v_1_able(e2,x3)])",
            "Enabled": true,
            "ID": "efc994a2-94b6-481e-9f75-c09efc44d352"
        },
        {
            "Command": "give me a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "4fb8afbc-08b7-4fa4-8a91-00cd6094a63d"
        },
        {
            "Command": "will you give me a table?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "887398ed-4865-411d-a59f-251fc53b4002"
        },
        {
            "Command": "You will give me a table",
            "Expected": "I don't understand the way you are using: give",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "d9773e57-08fb-4df3-9897-2891b1aa2b84"
        },
        {
            "Command": "Can we sit down?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _sit_v_down_able(e2,x3)])",
            "Enabled": true,
            "ID": "1a4bbc05-6aee-4462-b9fb-c944eb2d5257"
        },
        {
            "Command": "Let's get a table",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x9,_table_n_1(x9),pronoun_q(x5,pron(x5),_get_v_1(e2,x5,x9)))",
            "Enabled": true,
            "ID": "45f7c9b4-b7be-4538-bef7-ba834de8f293"
        },
        {
            "Command": "Let's go with a table",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x10,_table_n_1(x10),pronoun_q(x5,pron(x5),_want_v_1(e2,x5,x10)))",
            "Enabled": true,
            "ID": "7e20872c-bf6e-408e-94ab-61db6e66970d"
        },
        {
            "Command": "Let's get a table for two, please",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x9,number_q(x15,card(2,x15,i21),[_table_n_1(x9), _for_p(e14,x9,x15)]),pronoun_q(x5,pron(x5),[_please_a_1(e22,e2), _get_v_1(e2,x5,x9)]))",
            "Enabled": true,
            "ID": "d230cfe4-dc43-4d40-848b-c23b185eb602"
        },
        {
            "Command": "I will have a table?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "91cc802b-2e88-4fcb-a251-26c5e6f88f68"
        },
        {
            "Command": "Who will have a table?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "which_q(x3,person(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c902a6e5-53ff-409f-ba7c-08d63590b422"
        },
        {
            "Command": "Will you have a table?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c09676b8-c43a-4e18-8a90-109e288eea32"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "7717fbcf-b6e4-4e72-b8a8-75070cf34374"
        },
        {
            "Command": "Do you have the table?",
            "Expected": "I'm not sure which table you mean.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cd3fae35-7dac-447a-bb2a-94230d411ed1"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "40f0f35a-9eed-4fc8-8e91-23f968ff3009"
        },
        {
            "Command": "What can I have?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e15), _have_v_1_able(e2,x3,x5)]))",
            "Enabled": true,
            "ID": "324c870d-e826-4cdb-a4da-a209a1af334d"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2984c240-567b-479f-9aa3-07c8abc18995"
        },
        {
            "Command": "Can we have a table?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "817eaf3e-c2e5-4f6f-8953-812247c528ed"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "1a942f1b-375f-4421-9a2b-9856f666f7b6"
        },
        {
            "Command": "a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "_a_q(x4,_table_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "b37ddc44-76f4-41e4-9073-9d1760ae43c1"
        },
        {
            "Command": "Johnny and me",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x15,pron(x15),udef_q(x4,proper_q(x9,named(Johnny,x9),_and_c(x4,x9,x15)),unknown(e2,x4)))",
            "Enabled": true,
            "ID": "10093ffa-58d5-494c-843e-43fe0e6e5b5a"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "de70bf4f-4d76-4bd6-887f-696f9bec8abf"
        },
        {
            "Command": "a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "_a_q(x4,_table_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "9b7614f6-b920-4508-9157-3981dc72b265"
        },
        {
            "Command": "My son Johnny and me",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x10,pronoun_q(x17,pron(x17),[_son_n_of(x10,i22), poss(e16,x10,x17)]),proper_q(x11,named(Johnny,x11),pronoun_q(x28,pron(x28),udef_q(x4,[_and_c(x4,x10,x28), appos(e9,x10,x11)],unknown(e2,x4)))))",
            "Enabled": true,
            "ID": "39f43c15-387a-47f3-9783-7474f41a453b"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2698d4e9-10aa-4e73-a6da-1813031add43"
        },
        {
            "Command": "a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "_a_q(x4,_table_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "c03122f5-b566-4c9f-bdb8-03f6f46f3c55"
        },
        {
            "Command": "just two",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "[number_q(x4,card(2,x4,i12),unknown(e2,x4)), _just_x_deg(e6,u7)]",
            "Enabled": true,
            "ID": "ce3be103-f9d0-45b2-a430-270082aa498c"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0c5d94c2-9a67-43d5-ab3d-43de440888a7"
        },
        {
            "Command": "a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "_a_q(x4,_table_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "df1281d1-2be5-46d6-961d-1727f66546c3"
        },
        {
            "Command": "Just two, my son Johnny and me.",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "udef_q(x7,def_explicit_q(x19,pronoun_q(x26,pron(x26),[_son_n_of(x19,i31), poss(e25,x19,x26)]),proper_q(x20,named(Johnny,x20),pronoun_q(x37,pron(x37),[_and_c(x7,x19,x37), appos(e18,x19,x20)]))),number_q(x4,card(2,x4,i13),[appos(e6,x4,x7), _just_a_1(e5,e2), unknown(e2,x4)]))",
            "Enabled": true,
            "ID": "e3951b1a-656b-4214-9a60-951be1ef4413"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "bf913033-2a48-41ff-bb83-c0299a893193"
        },
        {
            "Command": "I'd like a table for my son and me",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,udef_q(x17,def_explicit_q(x22,pronoun_q(x27,pron(x27),[_son_n_of(x22,i32), poss(e26,x22,x27)]),pronoun_q(x34,pron(x34),_and_c(x17,x22,x34))),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "569f6ea4-c643-4d90-9eca-eed604923296"
        },
        {
            "Command": "I'd like a table for Johnny and me",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,udef_q(x17,proper_q(x22,named(Johnny,x22),pronoun_q(x28,pron(x28),_and_c(x17,x22,x28))),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5e581819-0549-4c62-9d1e-b2bca7ab4d2b"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "7788cfb0-fd1c-49d4-a3e2-a44396b5feb0"
        },
        {
            "Command": "We want tables",
            "Expected": "Johnny: Hey, let's sit together alright?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "35492138-e4fb-4a43-8bb8-994924f6c1f9"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "12bd1de9-8b40-498f-9252-9c5b676c481c"
        },
        {
            "Command": "I want the table",
            "Expected": "I'm not sure which table you mean.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "74092d64-1466-4b30-bf1d-486e17005e9e"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9e6ae622-0ad0-4c95-bfa2-305454e96a5e"
        },
        {
            "Command": "I'd like a steak",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a steak when you have a table.",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "0b2e3855-cca5-4e43-8532-621909cc3094"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4990c50f-5277-430b-9226-e1a266de9db4"
        },
        {
            "Command": "I'd like a table for 1",
            "Expected": "Johnny: Hey! That's not enough seats!",
            "Tree": "_a_q(x11,number_q(x17,card(1,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2f76af1e-038e-4916-b76e-a5344c2ef260"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d5f8a208-b881-4dae-a1b6-5fdfe526a1fb"
        },
        {
            "Command": "I'd like a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "66b5319c-66be-4787-b97b-4db8ea2effe5"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "70e0d89a-bec4-40c5-858f-6e9fe40265f9"
        },
        {
            "Command": "I'd like a table for 3",
            "Expected": "I'm not sure which table for 3 thing you mean.",
            "Tree": "_a_q(x11,number_q(x17,card(3,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "17cdb00c-6f14-458d-a810-639281544c82"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f3bf7412-3428-4f09-9797-bdd3982a864e"
        },
        {
            "Command": "we want a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3213c6a6-304c-488d-a079-0e91fb0cc829"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9e1086d8-cfd2-4762-b52d-2e421301b1da"
        },
        {
            "Command": "I want a table",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "048a8073-5351-43db-8e7c-b103a7722a7f"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x4,card(2,x4,i10),unknown(e2,x4))",
            "Enabled": true,
            "ID": "d078a2ea-e17c-44c5-9110-2600cea1e097"
        },
        {
            "Command": "I would like a table",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b5cfa314-b577-44c0-888c-e79450771d13"
        },
        {
            "Command": "I would love a table",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "976882a9-8fa0-4af3-9c7b-eda65b712812"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "012004e1-846f-4602-89dd-770941d992a1"
        },
        {
            "Command": "seat me",
            "Expected": "\nHost: How many in your party?",
            "Tree": "pronoun_q(x8,pron(x8),pronoun_q(x3,pron(x3),_seat_v_cause(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8037fad3-b057-44f7-98d4-6a6a801bdb87"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "37dc54db-2285-467b-8a6c-5ecf0f80c47b"
        },
        {
            "Command": "can you seat me?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "pronoun_q(x11,pron(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _seat_v_cause_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "6504baec-0698-4d3e-a222-bd73c653588e"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3dc77694-e6a5-412d-8548-2e25d1655745"
        },
        {
            "Command": "may i have a table?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "e0f65cc6-7f59-4532-9409-5a1baf503bb9"
        },
        {
            "Command": "just two",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "[number_q(x4,card(2,x4,i12),unknown(e2,x4)), _just_x_deg(e6,u7)]",
            "Enabled": true,
            "ID": "a41bab5a-8931-44e4-9411-1712805f649e"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "c10021df-8606-4bac-a3cd-2b07463c0bb5"
        },
        {
            "Command": "A table for two, please!",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],[_please_a_1(e17,e2), unknown(e2,x4)]))",
            "Enabled": true,
            "ID": "e8bd5597-ff18-4f78-b784-9ca3cd615e93"
        }
    ],
    "ElapsedTime": 71.89331
}