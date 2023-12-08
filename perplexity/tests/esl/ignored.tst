{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "alright, could we have a table?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_all+right_a_1(i4,_a_q(x14,_table_n_1(x14),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x14))))",
            "Enabled": true,
            "ID": "5a55771f-2f05-4c41-b73e-b65a85145b1b"
        },
        {
            "Command": "ok, can we have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "_okay_a_1(i4,_a_q(x14,_menu_n_1(x14),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x14))))",
            "Enabled": true,
            "ID": "cf3d3f38-e5fc-47a2-adac-8f11cd307446"
        }
    ]
}