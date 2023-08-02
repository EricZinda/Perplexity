{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ca458224-ee3b-4026-abd1-162fdccae031"
        },
        {
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "7d0a0701-3153-4533-bce6-0e1c5edda19d"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8115a330-d89e-4a01-8905-e127a115e58a"
        },
        {
            "Command": "I want a table for my son",
            "Expected": "Johnny: Hey! That's not enough seats!",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),[_son_n_of(x14,i25), poss(e19,x14,x20)]),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "8ebb4a5c-69c6-4877-8109-472977c306ce"
        },
        {
            "Command": "we want a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5b26ca51-8ef4-43e1-9f2e-b353c414ac31"
        },
        {
            "Command": "my son and I want a table",
            "Expected": "Um... You're at a table. \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x13,pron(x13),pronoun_q(x20,pron(x20),_a_q(x25,_table_n_1(x25),udef_q(x3,def_explicit_q(x8,[_son_n_of(x8,i18), poss(e12,x8,x13)],_and_c(x3,x8,x20)),_want_v_1(e2,x3,x25)))))",
            "Enabled": true,
            "ID": "d6ef7231-fb35-45c6-b175-f3652d61118f"
        },
        {
            "Command": "I want a table for my son and me",
            "Expected": "Um... You're at a table. \nWaiter: Can I get you something to eat?",
            "Tree": "udef_q(x14,def_explicit_q(x19,pronoun_q(x24,pron(x24),[_son_n_of(x19,i29), poss(e23,x19,x24)]),pronoun_q(x31,pron(x31),_and_c(x14,x19,x31))),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "0f263ee1-ce54-4c19-92de-84b4853f719f"
        },
        {
            "Command": "my son and I want tables",
            "Expected": "I suspect you want to sit together.",
            "Tree": "pronoun_q(x13,pron(x13),pronoun_q(x20,pron(x20),udef_q(x25,_table_n_1(x25),udef_q(x3,def_explicit_q(x8,[_son_n_of(x8,i18), poss(e12,x8,x13)],_and_c(x3,x8,x20)),_want_v_1(e2,x3,x25)))))",
            "Enabled": true,
            "ID": "b9a0586b-14db-41d0-acd7-40142ebdc0fa"
        },
        {
            "Command": "what is a table for?",
            "Expected": "Host: Sorry, I'm not here to explain things to you ...",
            "Tree": "which_q(x5,thing(x5),_a_q(x3,_table_n_1(x3),_for_p(e2,x3,x5)))",
            "Enabled": true,
            "ID": "970ceb12-9c17-41e3-9f02-9d89f88b9552"
        },
        {
            "Command": "what is a table for 2?",
            "Expected": "table",
            "Tree": "which_q(x5,thing(x5),number_q(x14,card(2,x14,i20),_a_q(x3,[_table_n_1(x3), _for_p(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "594b7dbd-be33-41e2-af85-e763c66143cc"
        },
        {
            "Command": "I'd like tables for my son and I'",
            "Expected": "I suspect you want to sit together.",
            "Tree": "udef_q(x11,udef_q(x17,def_explicit_q(x22,pronoun_q(x27,pron(x27),[_son_n_of(x22,i32), poss(e26,x22,x27)]),pronoun_q(x34,pron(x34),_and_c(x17,x22,x34))),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": false,
            "ID": "cedf7d75-45ce-4d05-a74e-4e717b1ac5e7"
        },
        {
            "Command": "I want the salmon",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_salmon_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "0331458f-c733-4545-a0aa-fc8510f068df"
        }
    ]
}