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
            "Command": "hello. table for two",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!<end>Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))<end>number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "8ebeed4a-7b58-4cce-993e-1e78e8a6d3fd"
        },
        {
            "Command": "Ok.  I will order the Steak.  My son will have the green salad please.",
            "Expected": "Son: Wait, let's not order salad before we know how much it costs.<end>Son: Wait, let's not order salad before we know how much it costs.<end>Son: Wait, let's not order salad before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,[_salad_n_1(x15), _green_a_2(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],[_please_a_1(e21,e2), _have_v_1(e2,x3,x15)])))<end>pronoun_q(x9,pron(x9),_the_q(x15,[_salad_n_1(x15), _green_a_2(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],[_please_a_1(e21,e2), _have_v_1(e2,x3,x15)])))<end>pronoun_q(x9,pron(x9),_the_q(x15,[_salad_n_1(x15), _green_a_2(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],[_please_a_1(e21,e2), _have_v_1(e2,x3,x15)])))",
            "Enabled": true,
            "ID": "6e8f8d80-4670-407d-8254-235a6ae5de1d"
        },
        {
            "Command": "I'll have the grilled salmon, please. Do you have any vegetarian options?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.<end>Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8)))<end>pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "03be4d95-80c7-4970-9ae9-d9525820fcd8"
        },
        {
            "Command": "oh, good point, I suppose. How much are each of the specials?",
            "Expected": "I don't know the words: part_of<end>I don't know the words: part_of",
            "Tree": "None<end>None",
            "Enabled": true,
            "ID": "f6f8047d-e0bf-4326-8988-26aa6302f802"
        },
        {
            "Command": "I would like a hamburger.  My son would like something vegetarian.",
            "Expected": "Host: Sorry, I'm not sure which one you mean.<end>Host: Sorry, I'm not sure which one you mean.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_some_q(x18,[thing(x18), _vegetarian_a_1(e23,x18)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))<end>pronoun_q(x9,pron(x9),_some_q(x18,[thing(x18), _vegetarian_a_1(e23,x18)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "dbc9df4c-0f8b-461b-8414-ab9c8c9210a7"
        }
    ],
    "ElapsedTime": 4.95826
}