{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "we want to sit down",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down_request(e2,x3))",
            "Enabled": true,
            "ID": "c3bc4308-e42b-4db2-944b-55a5fe8c832a"
        },
        {
            "Command": "what do you have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "569947bf-6700-4565-aec0-7b0f83c677fb"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "cb23e458-9d38-437c-9600-1a35ca7e89ff"
        }
    ]
}