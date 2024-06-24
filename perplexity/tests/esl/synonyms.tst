{
    "WorldName": "esl",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "94c80c84-1f15-43f1-a7dc-3719748ef324"
        },
        {
            "Command": "Can we get menus?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "2e777252-fd2c-4b4a-bce6-d29ceaa60eef"
        },
        {
            "Command": "I'll take a table for 2",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: Can I get you anything else?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_take_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "aa481f07-57c0-4d49-8138-a6748fbad2d1"
        },
        {
            "Command": "we will take menus",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_menu_n_1(x8),_take_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8548f60e-cfe8-4cdd-b92d-6c95465ca488"
        }
    ],
    "ElapsedTime": 2.13994
}