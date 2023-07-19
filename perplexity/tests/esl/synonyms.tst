{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2f64a8c3-2e94-4e57-8887-ed66edba6bf1"
        },
        {
            "Command": "Can I get a table for 2?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_get_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "94c80c84-1f15-43f1-a7dc-3719748ef324"
        },
        {
            "Command": "Can we get menus?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_get_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2e777252-fd2c-4b4a-bce6-d29ceaa60eef"
        }
    ]
}