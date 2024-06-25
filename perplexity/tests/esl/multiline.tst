{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "05cf91e2-b1d4-4dc6-82b2-8614bd04382b"
        },
        {
            "Command": "table for 2, please",
            "Expected": "I don't know the way you used: for",
            "Tree": "None",
            "Enabled": true,
            "ID": "8ebeed4a-7b58-4cce-993e-1e78e8a6d3fd"
        },
        {
            "Command": "I want a table for two, please",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],[_please_a_1(e20,e2), _want_v_1(e2,x3,x8)])))",
            "Enabled": true,
            "ID": "00b42c70-d2fb-4eb7-811d-4494063303c0"
        },
        {
            "Command": "My son will have the green salad please.",
            "Expected": "Son: Wait, let's not order salad before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,[_salad_n_1(x15), _green_a_2(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],[_please_a_1(e21,e2), _have_v_1(e2,x3,x15)])))",
            "Enabled": true,
            "ID": "f70166d8-bec2-4d5e-9633-7bc1d1eb741e"
        },
        {
            "Command": "My son would like something vegetarian.",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_some_q(x18,[thing(x18), _vegetarian_a_1(e23,x18)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "f6f8047d-e0bf-4326-8988-26aa6302f802"
        }
    ],
    "ElapsedTime": 2.22196
}