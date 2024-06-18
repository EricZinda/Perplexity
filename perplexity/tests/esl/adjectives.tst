{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8f560020-3575-4937-b66d-353a3fa6e2af"
        },
        {
            "Command": "The soup is smoked",
            "Expected": "I'm not sure which thing you mean.",
            "Tree": "_the_q(x3,_soup_n_1(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "0494e3db-dfae-4a1f-aeeb-f08560e495b7"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "b93aa427-f664-451e-950f-d142ac3df72a"
        },
        {
            "Command": "do you have vegetarian food?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_food_n_1(x8), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fcd8d9d2-e8b1-4e34-9ea9-9a4fa25969be"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a0dad2a1-544d-4e1a-bec0-3f463f4b6a4d"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "81e06a8c-a1ca-4cee-a718-74d0885455cf"
        },
        {
            "Command": "how much is the green salad?",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,[_salad_n_1(x3), _green_a_2(e20,x3)],count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "b3ac7119-4e10-4a6f-80ee-66e9bbf9a4f4"
        },
        {
            "Command": "how much is the tomato soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,udef_q(x21,_tomato_n_1(x21),[_soup_n_1(x3), compound(e20,x3,x21)]),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "d189a743-e47c-409d-86e6-130647d194c6"
        },
        {
            "Command": "I want a green dish and a tomato dish, please!",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x13,[_dish_n_of(x13,i18), _green_a_2(e17,x13)],_a_q(x20,udef_q(x26,_tomato_n_1(x26),[_dish_n_of(x20,i31), compound(e25,x20,x26)]),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x20),[_please_a_1(e32,e2), _want_v_1(e2,x3,x8)]))))",
            "Enabled": true,
            "ID": "59291b86-c54a-4f8b-b8da-d380d7fed0e4"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a salad and soup for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "b5596cde-1097-4c46-9101-bb5534463c3b"
        },
        {
            "Command": "I have a green salad",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_salad_n_1(x8), _green_a_2(e13,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "53adcedd-3198-4849-a66b-5d44ff7f04f5"
        },
        {
            "Command": "I have a tomato soup",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x14,_tomato_n_1(x14),pronoun_q(x3,pron(x3),_a_q(x8,[_soup_n_1(x8), compound(e13,x8,x14)],_have_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "20232d68-23ea-4832-b9e0-3404f288d7a3"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9071a4e3-01d8-4452-b484-498ae0163de9"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "484a8e87-086c-4d49-a9c7-a5bd4f109aa9"
        },
        {
            "Command": "the salmon is grilled",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_salmon_n_1(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "53ba1fcf-81b1-4dc9-bca0-2735e71b1c93"
        },
        {
            "Command": "is the salmon grilled?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_salmon_n_1(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "ab1a2cce-d9ea-4f9d-917a-268f48cf72c9"
        },
        {
            "Command": "what is grilled?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "8ffbcbd5-8527-4e9c-8351-d8c413e3eb04"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "587635f9-4727-49de-9aaf-ffed4a6fa579"
        },
        {
            "Command": "what is grilled?",
            "Expected": "grilled salmon\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "ca2c198e-4b69-4a1d-a20d-bfa1dd9aa556"
        },
        {
            "Command": "what is green?",
            "Expected": "salad\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_green_a_2(e2,x3))",
            "Enabled": true,
            "ID": "5ba28507-ebf2-4738-b717-134c14c8cece"
        },
        {
            "Command": "the pork is smoked",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_pork_n_1(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "06920d5c-cc03-437a-9924-b5af58233f3e"
        },
        {
            "Command": "is the pork smoked?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_pork_n_1(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "81ff3323-9450-4546-9bd0-f07f2156fcab"
        },
        {
            "Command": "do you have the grilled salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _grill_v_1(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "00535794-2db5-44cc-9bb8-47c95f1bd988"
        },
        {
            "Command": "do you have the smoked pork",
            "Expected": "Son: Wait, let's not order pork before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_pork_n_1(x8), _smoke_v_1(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "356262cd-6d0e-4ea9-8f1d-7cb83a06ef11"
        },
        {
            "Command": "I want the grilled salmon",
            "Expected": "Son: Wait, we already spent $12 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _grill_v_1(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "07526a10-6eaa-43f9-b1ed-25f12369342a"
        },
        {
            "Command": "I want the smoked pork",
            "Expected": "Son: Wait, let's not order pork before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_pork_n_1(x8), _smoke_v_1(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9b022abb-9691-4bc6-8993-e8d8fbee0952"
        },
        {
            "Command": "what is smoked?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "7190456b-3675-4585-a9c2-b95e7f7e0760"
        },
        {
            "Command": "what is smoked?",
            "Expected": "smoked pork\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "6d0e52f0-86c7-407f-ad67-27a0286b1f62"
        },
        {
            "Command": "the chicken is roasted",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_chicken_n_1(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "d7de34b3-d2b0-45f9-81a9-464b49dfdad7"
        },
        {
            "Command": "is the chicken roasted?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_chicken_n_1(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "488094e5-e8d5-4eae-94f0-76d6bfbfec8c"
        },
        {
            "Command": "do you have the roasted chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_chicken_n_1(x8), _roast_v_cause(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9818d448-e378-4a12-9ab0-828be345f34b"
        },
        {
            "Command": "I want the roasted chicken",
            "Expected": "Son: Wait, we already spent $19 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_chicken_n_1(x8), _roast_v_cause(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a69bd72f-0a97-423e-98e8-2947e8d8d5ab"
        },
        {
            "Command": "what is roasted?",
            "Expected": "roasted chicken\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "affd8599-3ae9-43f7-bd7b-e53fb3eb7fcb"
        },
        {
            "Command": "what is vegetarian?",
            "Expected": "soup\nsalad\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "536f65a4-7a11-4838-92ab-ef6166f9472f"
        }
    ],
    "ElapsedTime": 13.03566
}