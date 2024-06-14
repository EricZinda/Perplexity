{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ca458224-ee3b-4026-abd1-162fdccae031"
        },
        {
            "Command": "we want to sit down",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down_request(e2,x3))",
            "Enabled": true,
            "ID": "c3bc4308-e42b-4db2-944b-55a5fe8c832a"
        },
        {
            "Command": "what do you have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "569947bf-6700-4565-aec0-7b0f83c677fb"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you anything else?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "cb23e458-9d38-437c-9600-1a35ca7e89ff"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "e8b1853a-d29e-436a-ae38-c9f25a20ffe0"
        },
        {
            "Command": "can i sit down?",
            "Expected": "Host: How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _sit_v_down_able(e2,x3)])",
            "Enabled": true,
            "ID": "18ac5796-4c38-4731-869d-2937736ac2b4"
        },
        {
            "Command": "two",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x4,card(2,x4,i10),unknown(e2,x4))",
            "Enabled": true,
            "ID": "08a0a47b-6c1a-4787-b5fe-87305fd9ac0f"
        }
    ],
    "ElapsedTime": 2.23831
}