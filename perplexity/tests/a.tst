{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "I'd like a table",
            "Expected": "How many in your party?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "1e80048b-0f0f-4d3b-9bd3-88468e8fe34c"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "udef_q(x4,[generic_entity(x4), card(2,e10,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "7468553a-0e89-44bf-950a-12ab5d805f84"
        }
    ]
}