{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a3cc4d3-60e5-48e4-a624-f63883ff0403"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "1880a138-af07-4949-8987-69dce82b538d"
        },
        {
            "Command": "my son wants steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_steak_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "4aba975f-b500-41e8-91e9-840acb6f3987"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fdacf2bb-8a92-4f6a-999e-79bf25c8b802"
        },
        {
            "Command": "what did we order",
            "Expected": [
                "chicken\nsteak",
                "steak\nchicken"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "aa2f35b6-f3a1-4152-af96-d84c3be87a7b"
        },
        {
            "Command": "Can I cancel my order?",
            "Expected": "Waiter: No problem! Let me know what you would like instead.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "27599b97-ed77-4328-aae2-47cd93688319"
        },
        {
            "Command": "Could I cancel my order?",
            "Expected": "Waiter: No problem! Let me know what you would like instead.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "e9ee1777-a400-43fe-a45c-6071f430831b"
        },
        {
            "Command": "My son wants chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_chicken_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "824f3e0b-6635-4443-9d28-cfd5a236ab1e"
        },
        {
            "Command": "What is Johnny's order?",
            "Expected": [
                "steak\nchicken",
                "chicken\nsteak"
            ],
            "Tree": "which_q(x5,thing(x5),def_explicit_q(x3,proper_q(x10,named(Johnny,x10),[_order_n_of(x3), poss(e19,x3,x10)]),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "51a34357-8292-4b2f-a8a4-70ea8e7b3db4"
        },
        {
            "Command": "Can Johnny cancel Johnny's order?",
            "Expected": "Waiter: No problem! Let me know what Johnny would like instead.",
            "Tree": "proper_q(x14,named(Johnny,x14),def_explicit_q(x12,[_order_n_of(x12), poss(e23,x12,x14)],proper_q(x3,named(Johnny,x3),[event_replace(u99,e2,e11), _cancel_v_1_able(e2,x3,x12)])))",
            "Enabled": true,
            "ID": "cb96f3e5-22db-4d92-b848-10ba1ce864ad"
        },
        {
            "Command": "What is Johnny's order?",
            "Expected": "Nothing",
            "Tree": "which_q(x5,thing(x5),def_explicit_q(x3,proper_q(x10,named(Johnny,x10),[_order_n_of(x3), poss(e19,x3,x10)]),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "7c0aea6b-ae33-456b-87f3-aef8247da3b6"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5fa55642-7820-4bad-a0e1-7039ea015eb9"
        },
        {
            "Command": "Johnny wants chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x9,_chicken_n_1(x9),proper_q(x3,named(Johnny,x3),_want_v_1(e2,x3,x9)))",
            "Enabled": true,
            "ID": "e6ab7fca-6cd7-41c5-9ffc-7e5b3c12fc52"
        },
        {
            "Command": "Can you cancel our order?",
            "Expected": "Waiter: No problem! Let me know what you and Johnny would like instead.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "1e6e3c7e-0959-4bac-93d6-bd5c19b6f7b6"
        },
        {
            "Command": "What is our order?",
            "Expected": "Nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_order_n_of(x3), poss(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "eab39e04-d9a1-4a84-ab47-8a955355e66c"
        },
        {
            "Command": "Can Johnny cancel his order?",
            "Expected": "Waiter: No problem! Let me know what Johnny would like instead.",
            "Tree": "def_explicit_q(x12,pronoun_q(x18,pron(x18),[_order_n_of(x12), poss(e17,x12,x18)]),proper_q(x3,named(Johnny,x3),[event_replace(u99,e2,e11), _cancel_v_1_able(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "8979dc57-2c4a-4a77-bbc2-6340ba4a94c6"
        },
        {
            "Command": "You want to cancel my order",
            "Expected": "I'm not sure what that means.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),_cancel_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "9a1c3395-a7e6-4f4e-bd7d-0b086c2c188d"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9f9a18b4-9a2a-43ed-9a4e-7b0be08ec2a1"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "5857d78f-fa9d-4551-af71-b88260c36c56"
        },
        {
            "Command": "how much is the soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "c1d523ec-7a6e-4477-95c4-a90161b3c98f"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "c34d8395-d3a2-45d8-8564-e17f9e14f693"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5865b8ea-3730-4e7e-9f0c-ad8fcd9efd0a"
        },
        {
            "Command": "what did we order",
            "Expected": [
                "chicken\nsoup",
                "soup\nchicken"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f13adba2-77f5-4c66-8a56-31ba14ec0b26"
        },
        {
            "Command": "can my son start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x10,pron(x10),def_explicit_q(x3,[_son_n_of(x3,i15), poss(e9,x3,x10)],[event_replace(u99,e2,e17), _start_v_over_able(e2,x3)]))",
            "Enabled": true,
            "ID": "a76a2269-48fc-4c97-bf9d-5cd0e63e8cba"
        },
        {
            "Command": "what did I order",
            "Expected": "chicken",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "aa70e474-70e8-4c3c-9d95-f591a8906b6b"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "9a979384-9e3a-4734-91a8-fcc0777c1962"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "cd90a597-6821-45fb-b65c-564157c4597c"
        },
        {
            "Command": "can we start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "9a34c284-6dda-426f-86a7-fc17d97b0258"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a4b5e42c-e427-4877-8fde-0b95a9ec949a"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "f8da4a84-5816-40eb-b9a7-ddb765b10aa0"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "8df1861a-c314-4cf0-baec-47b6e5afcab9"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d84c6a2c-4283-454e-80f1-612d9a3d65c9"
        },
        {
            "Command": "could we start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "4cda3658-8a91-4bed-aa59-f887e4dc135d"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "20e138da-2adf-469a-9b09-cc41c87d3f70"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "3b5c662a-9cb0-49f2-b059-8b938ebd7a22"
        },
        {
            "Command": "can you start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "e92b611c-e75e-4bf3-9a0a-66ed90134583"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "30bfbe73-9bfa-4ca8-bb8c-8548f95bcd3d"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "f037ab19-ceb5-4acd-972e-15dcadada49e"
        }
    ],
    "ElapsedTime": 16.35717
}