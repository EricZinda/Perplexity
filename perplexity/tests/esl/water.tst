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
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "184bd202-1809-467b-8498-34860434b626"
        },
        {
            "Command": "I want water",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_water_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "19372455-ad78-4391-be80-e6cd47a34971"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a water for you.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "985e2f29-ef3e-4051-9286-1ccce5ccb417"
        },
        {
            "Command": "I have water",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_water_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "941cf9c7-5b82-4e83-8f12-8d3317c09486"
        },
        {
            "Command": "my son has water",
            "Expected": "son did not have water  \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_water_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_have_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "cb15454a-2a0f-4080-a4f2-654ad1524068"
        },
        {
            "Command": "I want water for my son",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),[_son_n_of(x14,i25), poss(e19,x14,x20)]),pronoun_q(x3,pron(x3),udef_q(x8,[_water_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a5a101ba-c8f4-4e98-ae9c-f49ef5924726"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a water for Johnny.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "69804b85-8e4b-4272-b056-313fade47006"
        },
        {
            "Command": "my son has water",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_water_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_have_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "1d51edd0-6092-45bb-9141-d073f4e59aca"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "942219a3-7bb8-4321-9f79-589525b604ed"
        },
        {
            "Command": "I want water",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a water when you have a table.\n",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_water_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f1d009bf-72a4-44ea-8b32-1c743a4e3127"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "38cda81d-5f7c-4f82-b2a8-d673e0bbae22"
        },
        {
            "Command": "I want water and a menu",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x13,_water_n_1(x13),_a_q(x18,_menu_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "fb5fb222-b8d0-4558-b3e5-26edf1e9366c"
        }
    ],
    "ElapsedTime": 8.92504
}