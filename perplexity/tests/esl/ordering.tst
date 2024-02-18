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
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e679d41e-af04-4f80-8192-5cbf08eb33af"
        },
        {
            "Command": "please bring us two glasses of water",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x11,pron(x11),udef_q(x10,udef_q(x22,_water_n_1(x22),[_glass_n_of(x10,x22), card(2,e21,x10)]),pronoun_q(x3,pron(x3),[polite(please,i5,e2), _bring_v_1(e2,x3,x10,x11)])))",
            "Enabled": true,
            "ID": "a7408b9b-7dc9-4d73-9006-0d37d4ffff0d"
        },
        {
            "Command": "what did I order?",
            "Expected": "water",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a267e43b-17ce-4e94-a258-96cdf2e20b7a"
        },
        {
            "Command": "what did Johnny order?",
            "Expected": "water",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "3e8edf8d-ab16-4c70-a35b-9976843a11e3"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a0783c0-04b9-4990-8653-98e906ba16b0"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "f2f7633a-d123-4e52-b0d6-af830a69a9b5"
        },
        {
            "Command": "Bring us 2 waters",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_water_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_bring_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "dfdd495d-5d82-49d9-bc95-bed3e6ebdf20"
        },
        {
            "Command": "what did I order?",
            "Expected": "water",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "50a55616-d99a-40dd-8a75-5328ff185b89"
        },
        {
            "Command": "what did Johnny order?",
            "Expected": "water",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "7d357afa-69a1-4002-a3a3-b224f8724807"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b406e76b-f802-4423-a953-fc8b9931a8e3"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "5e83ae9f-8377-430d-9ff6-4afd4325a537"
        },
        {
            "Command": "/runparse 2, 39",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "ef623ff4-31ff-438d-8db0-0cb8e796ae0a"
        },
        {
            "Command": "We'd like to start with some water and menus",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "_some_q(x15,udef_q(x20,_water_n_1(x20),udef_q(x25,_menu_n_1(x25),_and_c(x15,x20,x25))),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "2ef6be00-e7ea-44a9-b73f-aea220402f94"
        },
        {
            "Command": "/runparse",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "_some_q(x15,udef_q(x20,_water_n_1(x20),udef_q(x25,_menu_n_1(x25),_and_c(x15,x20,x25))),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "020cfae6-cf77-48ff-9de7-925f06821531"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "menu\nwater",
                "water\nmenu"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "c0f905da-c912-4070-9ed4-9e880e042617"
        },
        {
            "Command": "What did my son order?",
            "Expected": "water",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "b076a0b6-5b3c-431c-afef-bb7a74b42df0"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2beacbb1-7cfc-40dd-9c08-cbfd6d3a1e32"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "82f05ce5-dc43-4d84-915d-0d2a6821eb25"
        },
        {
            "Command": "We'd like to start with some water",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_some_q(x15,_water_n_1(x15),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "f99c7d3f-1ff8-4dc5-889c-e91860d64df0"
        },
        {
            "Command": "Can we have some menus?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "_some_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "7a4b134b-3dcd-4290-a657-18dc3f2ed059"
        },
        {
            "Command": "I want some steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_some_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4d11a206-7c07-42b2-91f5-6078d56e70dc"
        },
        {
            "Command": "how much is some soup?",
            "Expected": "4 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x10,abstr_deg(x10),_some_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "e1240d1a-31dd-47cc-af00-bf2d0579b5c1"
        },
        {
            "Command": "I want some soups",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_some_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1cb2c6e6-bab2-40d7-84b3-70f090e25a74"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "2 soup\nwater\nsteak\nmenu",
                "water\nsteak\n2 soup\nmenu",
                "2 soup\nsteak\nmenu\nwater",
                "steak\nmenu\n2 soup\nwater",
                "water\n2 soup\nmenu\nsteak",
                "2 soup\nwater\nmenu\nsteak",
                "2 soup\nmenu\nwater\nsteak",
                "steak\n2 soup\nmenu\nwater",
                "steak\nwater\n2 soup\nmenu",
                "steak\n2 soup\nwater\nmenu"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "25fdf234-2ed3-435b-ab80-fb10e5389462"
        },
        {
            "Command": "What did my son order?",
            "Expected": [
                "water\nmenu",
                "menu\nwater"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "daf4a340-1126-4f27-b87c-233dd8d3ba17"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "we'd like to start with a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x15,_table_n_1(x15),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "4a436537-1f34-4de5-8e2b-a4cb177c7605"
        },
        {
            "Command": "What did I order?",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e9ec6d48-008b-4c51-82e2-3f8d8b844b2c"
        },
        {
            "Command": "What did Johnny order?",
            "Expected": "Johnny ordered nothing",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "b202f65f-9778-4423-a925-395e1b0d8252"
        },
        {
            "Command": "What did we order?",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "8171037c-ba30-42bd-a9ce-ca63459df3c3"
        },
        {
            "Command": "I ordered a steak",
            "Expected": "you did not order a steak  \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "13ce708f-ec2a-41f8-b2dd-416711a3b810"
        },
        {
            "Command": "I can have a steak",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "84e4fc9b-4d71-4538-8561-36449163906c"
        },
        {
            "Command": "Who can have a steak?",
            "Expected": "you\n(among others)",
            "Tree": "which_q(x3,person(x3),_a_q(x11,_steak_n_1(x11),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "121251c1-efe2-47b5-a25f-a08648a34b5d"
        },
        {
            "Command": "What can I have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x5)))",
            "Enabled": true,
            "ID": "9a9c9df7-aa60-4471-8afc-113bc4b32488"
        },
        {
            "Command": "I'd like to start with a steak and a soup",
            "Expected": "Waiter: steak is an excellent choice!\nSon: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x15,_a_q(x20,_steak_n_1(x20),_a_q(x25,_soup_n_1(x25),_and_c(x15,x20,x25))),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "95ee387b-e08d-4263-b95e-a8f250546df3"
        },
        {
            "Command": "Can I have a steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "30071c2b-e13e-4ff0-9fa8-fea5b58b1873"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "2 steak\nmenu",
                "menu\n2 steak"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e0b92b58-14c2-40f2-a985-d36a356ed8dd"
        },
        {
            "Command": "I ordered the steak",
            "Expected": "Yes, that is true.(there are more)",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "10f63f95-11f4-48d0-b722-94c8bc3e5d53"
        },
        {
            "Command": "I ordered 2 steaks",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e966e46f-9893-46de-a53c-efc026cafe28"
        },
        {
            "Command": "What did we order?",
            "Expected": "Less than 2 people did that.",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "6e8ad609-7795-4d5c-96cd-cca160cf9f4e"
        },
        {
            "Command": "I will have a steak?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "73af9f66-e9d0-487a-9816-a582f7c3332f"
        },
        {
            "Command": "I will have a steak",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "76c09b78-40f9-4d01-ab0f-c7b9bd8946d9"
        },
        {
            "Command": "I'll start with a steak",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x9,_steak_n_1(x9),pronoun_q(x3,pron(x3),[_with_p(e8,e2,x9), _start_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "d0bd68b7-26e9-4575-ac55-49b7178169b1"
        },
        {
            "Command": "I will get the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_chicken_n_1(x8),_get_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "036118de-a9ab-429c-8d63-e65414a98b78"
        },
        {
            "Command": "I will have any meat",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_any_q(x8,_meat_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9a2a9945-3e16-4725-bf0a-b56918ade68a"
        },
        {
            "Command": "I'll take any meat dish",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x14,_meat_n_1(x14),pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8,i19), compound(e13,x8,x14)],_take_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a9bc7ac2-87d1-4d2d-b8f4-07b73c699cdd"
        },
        {
            "Command": "I will take the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_chicken_n_1(x8),_take_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d8ca1c3b-7a12-4913-8427-67c51d28ecb0"
        },
        {
            "Command": "Let's go with two orders of the Steak, please",
            "Expected": "Waiter: I'm sorry, we don't have enough steak for your order. \nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x10,_the_q(x17,_steak_n_1(x17),[_order_n_of(x10,x17), card(2,e16,x10)]),pronoun_q(x5,pron(x5),[_please_a_1(e22,e2), _want_v_1(e2,x5,x10)]))",
            "Enabled": true,
            "ID": "676c8863-4d33-4570-8141-145bbff1b417"
        },
        {
            "Command": "Let's have the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x9,_chicken_n_1(x9),pronoun_q(x5,pron(x5),_have_v_1(e2,x5,x9)))",
            "Enabled": true,
            "ID": "05db2218-cea5-4fcf-bd7d-25641a7261c8"
        },
        {
            "Command": "Let's go with the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x10,_chicken_n_1(x10),pronoun_q(x5,pron(x5),_want_v_1(e2,x5,x10)))",
            "Enabled": true,
            "ID": "ba113d31-5097-4ab5-a93b-a48b2b26ccdd"
        },
        {
            "Command": "I want an order of the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x13,_chicken_n_1(x13),pronoun_q(x3,pron(x3),_a_q(x8,_order_n_of(x8,x13),_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a44c27d7-6a35-4828-9925-0da3ee1f6cf6"
        },
        {
            "Command": "What do the steak and the soup cost?",
            "Expected": "steak : 10 dollars\nsoup : 4 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x5,thing(x5),_the_q(x13,_steak_n_1(x13),_the_q(x18,_soup_n_1(x18),udef_q(x3,_and_c(x3,x13,x18),_cost_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "988a743e-3192-46a0-8d3c-e20eaf3cfb4d"
        },
        {
            "Command": "What will the steak cost?",
            "Expected": "steak : 10 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_steak_n_1(x3),_cost_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a723cb98-7894-4702-a56d-4850d0c8f5c4"
        },
        {
            "Command": "The steak costs 10 dollars",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_steak_n_1(x3),udef_q(x8,[_dollar_n_1(x8,u15), card(10,e14,x8)],_cost_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "983116b0-36a9-4950-9d75-616087bb9061"
        },
        {
            "Command": "What did the steak cost?",
            "Expected": "I don't understand the way you are using: cost",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_steak_n_1(x3),_cost_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e4de925b-11c5-4c07-b11a-4896e6d9fc69"
        },
        {
            "Command": "You will have a steak?",
            "Expected": "I don't understand the way you are using: have",
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
            "Expected": "I don't understand the way you are using: have",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a004ac87-0ab4-4ec1-bf9a-1d1940231aa8"
        },
        {
            "Command": "Who will have a steak?",
            "Expected": "I don't understand the way you are using: have",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4f7dd64f-df78-46b5-8700-3b4e2c5097f5"
        },
        {
            "Command": "What are the specials?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "169a1146-bc00-4e1c-936c-cc2b903e3f46"
        },
        {
            "Command": "What specials do you have?",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "98667127-8757-4b90-9e2a-b4484844ad29"
        },
        {
            "Command": "What are your specials?",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_special_n_1(x3), poss(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "d122cc5c-a482-4b45-9345-0681627b6589"
        },
        {
            "Command": "Which dishes are specials?",
            "Expected": "pork\nsoup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "082d7d3e-6087-44b3-907b-3b1c6f46348c"
        },
        {
            "Command": "Which two dishes are specials?",
            "Expected": "pork\nsoup\n(among others)\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i11), card(2,e10,x5)],udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e8e03861-59c8-4f05-b5db-c88d3646a572"
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b4d472d4-4e03-4787-9360-8cf5a2920847"
        },
        {
            "Command": "I want a salad",
            "Expected": "Son: Wait, let's not order salad before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ee8d866-b726-444f-9abd-ba2db97f8caf"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2e558271-ef87-41e2-a5ba-d67ea0b5e4a3"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ac9ca7b7-60b3-4d02-8b03-9fa62fb80095"
        },
        {
            "Command": "My son would like a salmon",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x18,_salmon_n_1(x18),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "603ebce5-dcab-45a3-abdd-df45f4106a1b"
        },
        {
            "Command": "Johnny would love the salmon",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x12,_salmon_n_1(x12),proper_q(x3,named(Johnny,x3),_want_v_1(e2,x3,x12)))",
            "Enabled": true,
            "ID": "99d72ecb-d330-4bc9-bc81-17c870cf26c8"
        },
        {
            "Command": "Can we get one soup for Johnny, please?",
            "Expected": "Son: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x11,proper_q(x19,named(Johnny,x19),[_soup_n_1(x11), _for_p(e18,x11,x19), card(1,e17,x11)]),pronoun_q(x3,pron(x3),[_please_a_1(e25,e2), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "b3589252-e0bf-4534-8bfa-c2d079bc4700"
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "8d7e82ba-9d89-46b2-8532-8ca326bea794"
        },
        {
            "Command": "I would like the salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything else?",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5463c147-27e5-4920-934b-c6bfddc3741c"
        },
        {
            "Command": "How much is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "0c66d40d-000d-4f44-b15b-ec79e5bd018a"
        },
        {
            "Command": "How many dollars is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x9,abstr_deg(x9),_the_q(x3,_soup_n_1(x3),count(e14,x9,x5,udef_q(x5,_dollar_n_1(x5,u16),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "bf8680e8-0acf-42da-93c5-defa879f7f10"
        },
        {
            "Command": "How much is the salad?",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "5d7616ff-0fe6-482a-a57b-67ea07f9cf72"
        },
        {
            "Command": "I would like the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "7a84fe83-a358-4884-932d-cf00e69eb5bb"
        },
        {
            "Command": "I would like the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ad7a56d1-f75d-4cef-9649-99aa5aaae31d"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "soup\nsalad",
                "salad\nsoup"
            ],
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
            "Command": "How much are the dishes?",
            "Expected": "10 dollars\n7 dollars\n12 dollars\n8 dollars\n4 dollars\n3 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_dish_n_of(x3,i20),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "e13e91ec-7395-4c36-a509-3296ec3d427c"
        },
        {
            "Command": "How much are the specials?",
            "Expected": "4 dollars\n3 dollars\n8 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_special_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "ca595830-25f1-4b1b-a74e-3d47e4515acd"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2724f690-0b1e-47ab-823a-d712c996622c"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "34976bba-3203-4639-a0eb-68903a90ca33"
        },
        {
            "Command": "How much do the specials cost?",
            "Expected": "4 dollars\n3 dollars\n8 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_special_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_cost_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "6085ec6b-9636-47db-bb63-03192fe8605f"
        },
        {
            "Command": "I want soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "888ee475-5cac-4f92-87b5-8a04d7b0fed0"
        },
        {
            "Command": "I want salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "6f10abe3-2b46-47fc-8fec-63bccadb36bb"
        },
        {
            "Command": "I want pork",
            "Expected": "Waiter: pork is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_pork_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "59a2e11f-c5cd-4613-9628-7ffb6d53cee2"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "24b825d2-634c-43c8-97f9-038a5fbb2829"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "bf163c10-e572-44eb-b403-6d2ef7a2073b"
        },
        {
            "Command": "I want 3 steaks",
            "Expected": "Son: Wait, we already spent $0 so if we get 3 steak, we won't be able to pay for it with $20.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(3,e14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f412ffe0-207b-4b36-b8a4-b4e541ff3817"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "18d4ddaa-a0b5-4c6e-be76-f52dc41dda77"
        },
        {
            "Command": "I ordered 3 steaks",
            "Expected": "you did not order 3 steak  \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(3,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "326fcaba-7595-4143-9309-9142c06b5607"
        },
        {
            "Command": "soup and salad are vegetarian dishes",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x13,_salad_n_1(x13),udef_q(x18,[_dish_n_of(x18,i24), _vegetarian_a_1(e23,x18)],udef_q(x3,udef_q(x8,_soup_n_1(x8),_and_c(x3,x8,x13)),_be_v_id(e2,x3,x18))))",
            "Enabled": true,
            "ID": "a294ee3b-dfbd-4801-a01f-1b5ad96f4ff3"
        }
    ]
}