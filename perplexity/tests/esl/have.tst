{
    "WorldName": "esl",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "9f7092e1-f583-4537-a746-5276804ae76a"
        },
        {
            "Command": "Do I have a son?",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_son_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f8fa4a7-85dd-4be5-a9fe-e0ee0cfe1e43"
        },
        {
            "Command": "Do you have a steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "805b7349-7c9a-4e6f-af21-c51e1ef16da5"
        },
        {
            "Command": "Will I have a steak?",
            "Expected": "I don't understand the way you are using: have\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2cf3ed05-a5ad-4137-bc23-b1b39924a5e4"
        },
        {
            "Command": "Do you have the steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "96fa2577-6b6e-489e-9139-d68dc0ee0c32"
        },
        {
            "Command": "Do you have the table?",
            "Expected": "Yes.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5228b43a-2306-4599-9955-09dbb3a7b2c1"
        },
        {
            "Command": "do you have specials?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_special_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f4c1ab20-f754-4c15-8c2c-af2c647bf722"
        },
        {
            "Command": "what do I have?",
            "Expected": [
                "Johnny\nbill\norder\nWaiter: Can I get you anything besides 2 steaks for you?",
                "bill\nJohnny\norder\nWaiter: Can I get you anything besides 2 steaks for you?",
                "Johnny\norder\nbill\nWaiter: Can I get you anything besides 2 steaks for you?",
                "order\nbill\nJohnny\nWaiter: Can I get you anything besides 2 steaks for you?",
                "order\nJohnny\nbill\nWaiter: Can I get you anything besides 2 steaks for you?",
                "bill\norder\nJohnny\nWaiter: Can I get you anything besides 2 steaks for you?"
            ],
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
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "16d05530-68d8-4d9a-85da-e17e918b1ac9"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Host: If you'd like to hear about our menu items, you'll need to have a seat.\nHost: How can I help you today?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "1cb0a35e-2a96-4ba5-84d2-59d10c0d82e9"
        },
        {
            "Command": "do you have the menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "187818d5-ec88-45e4-8076-b0edacf380a6"
        },
        {
            "Command": "do you have the bill?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a bill when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_bill_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5f3e6faf-3774-43b0-a186-eeb07b6a9be5"
        },
        {
            "Command": "do you have a bill?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a bill when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_bill_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c89788d2-274d-4547-8eba-67cfd08c89ea"
        },
        {
            "Command": "do you have steaks?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a steak when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3b0cc457-bd68-46c2-812c-26e4ae55b3b2"
        },
        {
            "Command": "who has steaks?",
            "Expected": "Host: Nobody.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "dabd14d7-0d27-4eaa-bc91-48236d7ee0b6"
        },
        {
            "Command": "what has steaks?",
            "Expected": "restaurant\nHost: How can I help you today?",
            "Tree": "which_q(x3,thing(x3),udef_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ba7fbf08-8c07-4316-ae1f-2fa1a21c91c1"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8c4661e6-0e04-4ea9-9928-dd8b38a8bac1"
        },
        {
            "Command": "do you have a table?",
            "Expected": "Yes.\nHost: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b1192b76-dc74-437d-aeac-811d21e7b0b6"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "807fb862-60f4-47a6-8b1b-a4dcfb74a8ae"
        },
        {
            "Command": "do you have the table",
            "Expected": "I'm not sure which table you mean.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d08e91ef-3bcd-42b0-a0dc-8c7d1a357a51"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "7a9a9c26-3451-4bd0-a554-415693955e1f"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "1f24c6c3-e897-48af-a08e-45353824ead3"
        },
        {
            "Command": "do you have this table",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_this_q_dem(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5e36dbc8-a912-4c92-9878-9ed8de615bfd"
        },
        {
            "Command": "do you have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "77f79c20-8150-4761-815b-eea143af6942"
        },
        {
            "Command": "do you have menus?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cc1fb4b4-ee23-4700-b941-9762d19170ec"
        },
        {
            "Command": "do you have 2 menus?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(2,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f381604d-5871-4901-b789-faa5d0e83064"
        },
        {
            "Command": "No",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a menu for you.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "9192da64-3bda-4261-a479-2bd7517617e9"
        },
        {
            "Command": "Do I have a menu?",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "73c3f31c-5793-45a6-a3ac-ebf2cd8d9a6c"
        }
    ],
    "ElapsedTime": 38.03707
}