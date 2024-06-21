{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "Hi!",
            "Expected": "Hello!",
            "Tree": "proper_q(x4,named(Hawaii,x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "5a55771f-2f05-4c41-b73e-b65a85145b1b"
        },
        {
            "Command": "Hello!",
            "Expected": "Hello!",
            "Tree": "proper_q(x4,named(Hawaii,x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "b00d2816-95d2-4e45-8340-636658ee6264"
        },
        {
            "Command": "alright, could we have a table?",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_all+right_a_1(i4,_a_q(x14,_table_n_1(x14),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _have_v_1_able(e2,x3,x14)])))",
            "Enabled": true,
            "ID": "c1b2d49d-7d2e-4003-9dea-d43f04a6a3a8"
        },
        {
            "Command": "ok, can we have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "_okay_a_1(i4,_a_q(x14,_menu_n_1(x14),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e13), _have_v_1_able(e2,x3,x14)])))",
            "Enabled": true,
            "ID": "cf3d3f38-e5fc-47a2-adac-8f11cd307446"
        }
    ],
    "ElapsedTime": 1.52846
}