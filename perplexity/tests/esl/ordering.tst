{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4a436537-1f34-4de5-8e2b-a4cb177c7605"
        },
        {
            "Command": "What did I order?",
            "Expected": "Nothing. \nWaiter: Can I get you something to eat?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e9ec6d48-008b-4c51-82e2-3f8d8b844b2c"
        },
        {
            "Command": "What did my son order?",
            "Expected": "Nothing. \nWaiter: Can I get you something to eat?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "b202f65f-9778-4423-a925-395e1b0d8252"
        },
        {
            "Command": "What did we order?",
            "Expected": "Nothing. \nWaiter: Can I get you something to eat?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "8171037c-ba30-42bd-a9ce-ca63459df3c3"
        },
        {
            "Command": "I ordered a steak",
            "Expected": "No. you does not order steak  \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "13ce708f-ec2a-41f8-b2dd-416711a3b810"
        },
        {
            "Command": "I can have a steak",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "84e4fc9b-4d71-4538-8561-36449163906c"
        },
        {
            "Command": "Who can have a steak?",
            "Expected": "you(there are more)",
            "Tree": "which_q(x3,person(x3),_a_q(x11,_steak_n_1(x11),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "121251c1-efe2-47b5-a25f-a08648a34b5d"
        },
        {
            "Command": "What can I have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x5)))",
            "Enabled": true,
            "ID": "9a9c9df7-aa60-4471-8afc-113bc4b32488"
        },
        {
            "Command": "I want a steak and a soup",
            "Expected": "One thing at a time, please!",
            "Tree": "_a_q(x13,_steak_n_1(x13),_a_q(x18,_soup_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "95ee387b-e08d-4263-b95e-a8f250546df3"
        },
        {
            "Command": "Can I have a steak?",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "30071c2b-e13e-4ff0-9fa8-fea5b58b1873"
        },
        {
            "Command": "What did I order?",
            "Expected": "steak",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e0b92b58-14c2-40f2-a985-d36a356ed8dd"
        },
        {
            "Command": "What did we order?",
            "Expected": "Nothing. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "6e8ad609-7795-4d5c-96cd-cca160cf9f4e"
        },
        {
            "Command": "I will have a steak?",
            "Expected": "I'm not sure what that means.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "73af9f66-e9d0-487a-9816-a582f7c3332f"
        },
        {
            "Command": "I will have a steak",
            "Expected": "Son: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "76c09b78-40f9-4d01-ab0f-c7b9bd8946d9"
        },
        {
            "Command": "What do the steak and the soup cost?",
            "Expected": "steak : 10 dollars\nsoup : 4 dollars",
            "Tree": "which_q(x5,thing(x5),_the_q(x13,_steak_n_1(x13),_the_q(x18,_soup_n_1(x18),udef_q(x3,_and_c(x3,x13,x18),_cost_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "988a743e-3192-46a0-8d3c-e20eaf3cfb4d"
        },
        {
            "Command": "You will have a steak?",
            "Expected": "I'm not sure what that means.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "37a62861-89f7-4aa7-ab60-7fbff5ad071d"
        },
        {
            "Command": "You will have a steak.",
            "Expected": "I'm not sure what that means.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e80b2674-3527-4485-abc6-4368809ecb62"
        },
        {
            "Command": "What will I have?",
            "Expected": "I'm not sure what that means.",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a004ac87-0ab4-4ec1-bf9a-1d1940231aa8"
        },
        {
            "Command": "Who will have a steak?",
            "Expected": "I'm not sure what that means.",
            "Tree": "which_q(x3,person(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "74aa2bec-f3d0-457a-98f0-afbbd59e9f88"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4919a6c6-a36d-4c96-83fc-199d289eeb11"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4f7dd64f-df78-46b5-8700-3b4e2c5097f5"
        },
        {
            "Command": "What are the specials?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you something to eat?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "169a1146-bc00-4e1c-936c-cc2b903e3f46"
        },
        {
            "Command": "What specials do you have?",
            "Expected": "So again, we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you something to eat?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "98667127-8757-4b90-9e2a-b4484844ad29"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3683bdd4-f7e4-419c-bc16-f5df21f5cc41"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b4d472d4-4e03-4787-9360-8cf5a2920847"
        },
        {
            "Command": "I want a salad",
            "Expected": "Son: Wait, let's not order that before we know how much it costs. \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ee8d866-b726-444f-9abd-ba2db97f8caf"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2e558271-ef87-41e2-a5ba-d67ea0b5e4a3"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Son: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ac9ca7b7-60b3-4d02-8b03-9fa62fb80095"
        },
        {
            "Command": "My son would like a salmon",
            "Expected": "Son: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x18,_salmon_n_1(x18),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "603ebce5-dcab-45a3-abdd-df45f4106a1b"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "db0eb32b-5205-40e8-a821-35975d4668b5"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "8d7e82ba-9d89-46b2-8532-8ca326bea794"
        },
        {
            "Command": "I would like the salmon",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_salmon_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3003a1eb-14b6-4dfe-9fe9-496d3a3e44a1"
        },
        {
            "Command": "What did I order?",
            "Expected": "salmon",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "cbe31443-8b30-48e9-a530-a131548fa6b5"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2ba0af2c-9d36-4c23-abc3-9112283310d7"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5463c147-27e5-4920-934b-c6bfddc3741c"
        },
        {
            "Command": "How much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "0c66d40d-000d-4f44-b15b-ec79e5bd018a"
        },
        {
            "Command": "How much is the salad?",
            "Expected": "3 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "5d7616ff-0fe6-482a-a57b-67ea07f9cf72"
        },
        {
            "Command": "I would like the salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "7a84fe83-a358-4884-932d-cf00e69eb5bb"
        },
        {
            "Command": "I would like the soup",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ad7a56d1-f75d-4cef-9649-99aa5aaae31d"
        },
        {
            "Command": "What did I order?",
            "Expected": "soup\nsalad",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f04f7d4e-c918-4d46-81f0-a4bf4044dae4"
        },
        {
            "Command": "I ordered salad and soup",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x13,_salad_n_1(x13),udef_q(x18,_soup_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_order_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "bd6b1750-5480-4661-a1d6-600bb7dbbc2a"
        },
        {
            "Command": "I ordered the soup",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c3b2b4ed-9938-468a-8567-250e7833d15f"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a3cc4d3-60e5-48e4-a624-f63883ff0403"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e679d41e-af04-4f80-8192-5cbf08eb33af"
        },
        {
            "Command": "I want 2 steaks",
            "Expected": "Excellent Choice! Can I get you anything else?\nSon: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f412ffe0-207b-4b36-b8a4-b4e541ff3817"
        },
        {
            "Command": "what did I order",
            "Expected": "steak",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "18d4ddaa-a0b5-4c6e-be76-f52dc41dda77"
        },
        {
            "Command": "I ordered 2 steaks",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "326fcaba-7595-4143-9309-9142c06b5607"
        }
    ]
}