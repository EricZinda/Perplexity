{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "I'd like a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "1e80048b-0f0f-4d3b-9bd3-88468e8fe34c"
        },
        {
            "Command": "I want the menu",
            "Expected": "I'm sorry, we're all out of menus. \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "7468553a-0e89-44bf-950a-12ab5d805f84"
        }
    ]
}