{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5c0b3d20-fa58-4cf1-b9be-1c410f699704"
        },
        {
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "9f7092e1-f583-4537-a746-5276804ae76a"
        },
        {
            "Command": "Do I have a son?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_son_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f8fa4a7-85dd-4be5-a9fe-e0ee0cfe1e43"
        },
        {
            "Command": "Do you have a steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "805b7349-7c9a-4e6f-af21-c51e1ef16da5"
        },
        {
            "Command": "Do you have the steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "96fa2577-6b6e-489e-9139-d68dc0ee0c32"
        },
        {
            "Command": "Do you have the table?",
            "Expected": "I'm not sure which the table you mean",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5228b43a-2306-4599-9955-09dbb3a7b2c1"
        },
        {
            "Command": "do you have specials?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_special_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f4c1ab20-f754-4c15-8c2c-af2c647bf722"
        },
        {
            "Command": "what do I have?",
            "Expected": "your son",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ce0108a8-950a-408d-8e4b-ec61b6da04ce"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3d35b84b-7f51-4dae-bafe-6213461d09a6"
        },
        {
            "Command": "what do you have?",
            "Expected": "If you'd like to hear about our menu items, you'll need to have a seat.",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "16d05530-68d8-4d9a-85da-e17e918b1ac9"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "If you'd like to hear about our menu items, you'll need to have a seat.",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "1cb0a35e-2a96-4ba5-84d2-59d10c0d82e9"
        },
        {
            "Command": "do you have the menu?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "187818d5-ec88-45e4-8076-b0edacf380a6"
        },
        {
            "Command": "do you have the bill?",
            "Expected": "But... you haven't got any food yet!",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_bill_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5f3e6faf-3774-43b0-a186-eeb07b6a9be5"
        },
        {
            "Command": "do you have steaks?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3b0cc457-bd68-46c2-812c-26e4ae55b3b2"
        },
        {
            "Command": "who has steaks?",
            "Expected": "No. you does not have something ",
            "Tree": "which_q(x3,person(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "dabd14d7-0d27-4eaa-bc91-48236d7ee0b6"
        },
        {
            "Command": "what has steaks?",
            "Expected": "restaurant\n",
            "Tree": "which_q(x3,thing(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ba7fbf08-8c07-4316-ae1f-2fa1a21c91c1"
        }
    ]
}