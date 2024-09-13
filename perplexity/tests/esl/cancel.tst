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
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "05414b48-6673-4def-8422-ac616ab9cf7c"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3d1735d4-763b-4148-b063-780f0de7e401"
        },
        {
            "Command": "Cancel the steak I ordered",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x14,pron(x14),pronoun_q(x3,pron(x3),_the_q(x8,[_steak_n_1(x8), _order_v_1(e18,x14,x8)],_cancel_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "03c23b2b-5df1-4747-be7f-20524c7710db"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "866e2e26-4404-412a-b80f-95968472d9dd"
        },
        {
            "Command": "Could you cancel the steak I ordered",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,pronoun_q(x17,pron(x17),[_steak_n_1(x11), _order_v_1(e21,x17,x11)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "ff029dcb-b4f7-456c-9074-8a99ae8488bc"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "886cbc6c-61d1-4f5b-9982-a63905ab0b33"
        },
        {
            "Command": "Can you cancel the steak I ordered",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,pronoun_q(x17,pron(x17),[_steak_n_1(x11), _order_v_1(e21,x17,x11)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "1ad3ac05-25e0-4a16-97ed-81985578acd6"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "74716e8b-bc7b-4aca-9197-0485f52689a6"
        },
        {
            "Command": "Cancel the steak I requested",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x14,pron(x14),pronoun_q(x3,pron(x3),_the_q(x8,[_steak_n_1(x8), _request_v_1(e18,x14,x8)],_cancel_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "f785d958-1cb8-46e7-856d-6974c678d731"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "7873e315-fd55-452a-855b-70bc576689f4"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "683377f6-2ddb-418a-8025-1e78b5366e29"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "148065bc-4eae-42ed-b59b-962d1800c61d"
        },
        {
            "Command": "I don't want steak anymore",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),[_anymore_a_1(e16,e10), event_replace(u99,e2,e10), _cancel_v_1(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "0107b0e2-625c-4c01-b47b-e802004a11f5"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8bd78b76-0fb6-4401-8b7d-a70abea6ad53"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "94d3ad53-f6b5-4ffb-a808-4579a7eef114"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "604f2afa-1fff-4516-b145-519dc36c4306"
        },
        {
            "Command": "Can we cancel my food?",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: Sorry, I don't believe I have that order.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_food_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "4290a110-2531-4102-bf1d-c32fcf5d8678"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "88782b3a-e67a-4099-816f-1b6e7b07144d"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "d9a38518-2f0e-4b15-b598-7ee3a52887d9"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fbd68b1a-e2d2-4459-9414-7894ffcda7a1"
        },
        {
            "Command": "cancel my steak order",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x14,pron(x14),udef_q(x20,_steak_n_1(x20),pronoun_q(x3,pron(x3),def_explicit_q(x8,[_order_n_of(x8), compound(e19,x8,x20), poss(e13,x8,x14)],_cancel_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "558316e5-356b-4283-aeca-923aaebfd58c"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "61e85ece-1910-46a6-a52b-c674d3665f72"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "302503be-c8a4-4c4e-8b6d-54cac46e0d79"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "97c09c5a-2f28-4f92-bf03-28623bac6e3a"
        },
        {
            "Command": "I'd like to cancel my steak order",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),udef_q(x26,_steak_n_1(x26),[_order_n_of(x14), compound(e25,x14,x26), poss(e19,x14,x20)])),pronoun_q(x3,pron(x3),_cancel_v_1_request(e13,x3,x14)))",
            "Enabled": true,
            "ID": "50a7ca7f-52ac-4a2d-bfbd-fcfa38876482"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "07cacb72-0dc4-45c8-89a9-2e93b753d023"
        },
        {
            "Command": "Could you please cancel my steak order?",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x12,pronoun_q(x18,pron(x18),udef_q(x24,_steak_n_1(x24),[_order_n_of(x12), compound(e23,x12,x24), poss(e17,x12,x18)])),pronoun_q(x3,pron(x3),[_please_a_1(e10,e11), event_replace(u99,e2,e11), _cancel_v_1_able(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "1b536c64-1022-4095-9fe9-553b7afb0f97"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "16111297-9a40-4378-83c2-5d33ba60f082"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "61bd215c-a354-4ee6-847e-a36f1602dfbd"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2c8c8896-759a-4026-acd1-6b9681745f34"
        },
        {
            "Command": "I want to cancel my steak order",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),udef_q(x23,_steak_n_1(x23),[_order_n_of(x11), compound(e22,x11,x23), poss(e16,x11,x17)])),pronoun_q(x3,pron(x3),_cancel_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "c9dd6f99-df8e-4804-842d-274bf44d841e"
        },
        {
            "Command": "I want steak and water",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: water is an excellent choice!\nWaiter: Can I get you anything besides a steak and a water for you?",
            "Tree": "udef_q(x13,_steak_n_1(x13),udef_q(x18,_water_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "94263e3e-da26-4157-8f09-f35ccef256e3"
        },
        {
            "Command": "I want to cancel my food order",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: Can I get you anything besides a water for you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),udef_q(x23,_food_n_1(x23),[_order_n_of(x11), compound(e22,x11,x23), poss(e16,x11,x17)])),pronoun_q(x3,pron(x3),_cancel_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "71db396a-3aa2-4b9d-8f14-436f2c0f6181"
        },
        {
            "Command": "what did I order?",
            "Expected": "water\nWaiter: Can I get you anything besides a water for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "db9d83d4-58fa-4fb9-9023-327381a75586"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ac78c8cb-e708-4ecb-9748-275c56f32244"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "438b2a36-ea30-4c23-9c3c-1c2ed53f778d"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c4e8c1d1-afe3-4182-bdb4-c2c44ee7b4d4"
        },
        {
            "Command": "I want to cancel my steak",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_steak_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),_cancel_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "28625d48-ab71-476e-8872-eb073ff93a48"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "13667943-2221-41b5-8a75-dee41004150a"
        },
        {
            "Command": "I want to cancel my order",
            "Expected": "Waiter: I have removed the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),_cancel_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3ab1c245-e533-420c-8ed4-d7be5b53d32d"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "887df412-8936-4667-b69b-cf460fe3602d"
        },
        {
            "Command": "Could I cancel my steak",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_steak_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "2b0c3bc3-8baf-449c-a4e5-521dcde2c82f"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b3026e92-63a3-470e-b5d6-622f96ea3e22"
        },
        {
            "Command": "Could I cancel my order",
            "Expected": "Waiter: I have removed the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "3d021e94-e8a1-472b-807b-8d8192084a75"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "54b932f5-9c94-498c-bc75-f380da341614"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "212d0c08-4aa3-42f7-bf62-54797dde7bc9"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "deaa1e2b-f78b-436e-b2ac-1ae6bb861278"
        },
        {
            "Command": "Can you cancel the steak?",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "96b53b1a-cfb2-40ae-bee4-25c4db214349"
        },
        {
            "Command": "I ordered a steak",
            "Expected": "a steak is not ordered.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3e4874e5-bf9c-4597-83b0-7aafafd0a21e"
        },
        {
            "Command": "how much is soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),udef_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "61d2c9e6-64e1-42a3-9914-7b44f37bec2c"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "6bf6d2c3-ee55-4a9d-9f9f-354195fa57e4"
        },
        {
            "Command": "can you cancel the soup for my son?",
            "Expected": "Waiter: I have removed a soup from the order for Johnny.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,def_explicit_q(x17,pronoun_q(x23,pron(x23),[_son_n_of(x17,i28), poss(e22,x17,x23)]),[_soup_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "7965167a-13e6-415c-8454-c618823d580b"
        },
        {
            "Command": "we want soups",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you and a soup for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fc0a369b-1ccc-48e5-a417-7c050872c042"
        },
        {
            "Command": "can you cancel the soups?",
            "Expected": "Waiter: I have removed a soup from the order for you and a soup from the order for Johnny.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "83f3ef6a-cb89-4f5b-bdfc-dd8122f5e3d1"
        },
        {
            "Command": "we want soups",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you and a soup for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1a0f577d-8d9e-4ef1-bb23-799b6d2a6f58"
        },
        {
            "Command": "can you cancel a soup?",
            "Expected": "Waiter: I have removed a soup from the order for you.\nWaiter: Can I get you anything besides a soup for Johnny?",
            "Tree": "_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "a78d6fee-afb5-4075-ac52-69c2cf5543ba"
        },
        {
            "Command": "can you cancel 2 soups",
            "Expected": "Waiter: I have removed a soup from the order for Johnny.\nWaiter: Sorry, I don't believe you've ordered 1 of the soup you want to cancel.\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,[_soup_n_1(x11), card(2,e17,x11)],pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "b43f0b8c-c373-4b88-8b54-4cfafd73873c"
        },
        {
            "Command": "can you cancel a soup",
            "Expected": "Waiter: Sorry, I don't believe I have that order.\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "df5c1b8d-5c1d-4b6a-b30d-913c162e20d1"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d12cda31-cf7b-4187-986e-afe4f626450d"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a steak for you and a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "ab0fa8c7-e4d4-46dd-9cdc-7da1e23a49d6"
        },
        {
            "Command": "can you cancel the steak and the soup",
            "Expected": "Waiter: I have removed a steak from the order for you and a soup from the order for Johnny.\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,_the_q(x16,_steak_n_1(x16),_the_q(x21,_soup_n_1(x21),_and_c(x11,x16,x21))),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "7dded3de-5d55-4ebb-a5eb-435e78a02406"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "6a3fd744-8f7e-44c9-b622-29ed557f1b83"
        },
        {
            "Command": "can I cancel the order?",
            "Expected": "Waiter: I have removed the order for you.\nWaiter: Sorry, I don't believe there is an order for Johnny.\nWaiter: Sorry, I don't believe there is an order for you and Johnny together.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,_order_n_of(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "76824b9c-a62c-45e7-89b7-08dec4c49371"
        },
        {
            "Command": "Can I cancel my order",
            "Expected": "Waiter: Sorry, I don't believe there is an order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "fbc708f0-b68e-478d-8f0a-150d448dc3b3"
        },
        {
            "Command": "Can I cancel our order",
            "Expected": "Waiter: Sorry, I don't believe there is an order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "679084ad-c7f3-42bd-b1fa-a97a12e6d66b"
        },
        {
            "Command": "Can I cancel the order for me",
            "Expected": "WRONG Waiter: Sorry, I don't believe there is an order for you.\nWaiter: Sorry, I don't believe there is an order for Johnny.\nWaiter: Sorry, I don't believe there is an order for you and Johnny together.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,pronoun_q(x17,pron(x17),[_order_n_of(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "342daede-7db9-493b-9481-3be490fbfbeb"
        },
        {
            "Command": "I want salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything besides a salmon for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_salmon_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "95391939-c921-495c-96cb-fa2577b61de4"
        },
        {
            "Command": "can I cancel the grilled item?",
            "Expected": "Waiter: I have removed a salmon from the order for you.\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,[_thing_n_of-about(x11,i18), _grill_v_1(e16,i17,x11)],pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "8bced605-d89d-42ce-854a-0ba4b5679c4f"
        },
        {
            "Command": "I want steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "436d4b39-b0b2-499c-a4a3-42bca3736caf"
        },
        {
            "Command": "can I cancel my steak?",
            "Expected": "Waiter: I have removed a steak from the order for you.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_steak_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "72f079b4-2e31-4cfd-9909-939303bc9bdf"
        },
        {
            "Command": "how much is soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),udef_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "7b20bd4d-64a6-4f7a-b552-3a69d9f7b3c7"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "5c47a154-cf8d-4855-9f39-8e3a52714e1a"
        },
        {
            "Command": "can I cancel my son's soup'",
            "Expected": "Waiter: I have removed a soup from the order for Johnny.\nWaiter: What can I get you?",
            "Tree": "def_explicit_q(x13,pronoun_q(x18,pron(x18),[_son_n_of(x13,i23), poss(e17,x13,x18)]),def_explicit_q(x11,[_soup_n_1(x11), poss(e28,x11,x13)],pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _cancel_v_1_able(e2,x3,x11)])))",
            "Enabled": true,
            "ID": "dc3ddfbd-85a7-4de8-afe5-bc7e4a29e3eb"
        }
    ]
}