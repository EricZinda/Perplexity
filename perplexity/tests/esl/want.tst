{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "09781c14-ff1a-4525-8e73-3652771694bb"
        },
        {
            "Command": "I want a table and some water",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a water when you have a table.\nHost: How many in your party?",
            "Tree": "_a_q(x13,_table_n_1(x13),_some_q(x18,_water_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "50eeae4c-6da0-46c7-bfb7-cd812b56a8c3"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0212ddb1-4bce-4c84-b846-c01e4de39818"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "099784a7-de4f-45b1-8c34-e6699afef139"
        },
        {
            "Command": "I want a menu and a steak",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x13,_menu_n_1(x13),_a_q(x18,_steak_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "71afb0e0-c566-4cb5-9994-9e03132f67f8"
        },
        {
            "Command": "no",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything else?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "007f54d8-0657-48b8-8960-0dc13f7e38b0"
        },
        {
            "Command": "I want a steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "60f8e4b6-a722-40f3-b40d-770b0b47ab51"
        },
        {
            "Command": "no",
            "Expected": "Johnny: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu? \nYou tell the waiter to ignore what you just ordered.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "64950a6d-1625-406e-bddc-b1550810dc60"
        },
        {
            "Command": "what did I order?",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a9aa1ba0-ec68-43bf-b2bc-06e075675499"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4aa93473-4563-47c6-a77d-5982e8638c74"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "cdacefe9-ea6c-4789-b011-38ca1066b6ac"
        },
        {
            "Command": "I want a menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d4b8b989-70b3-4489-9cbb-7d4c75d40363"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "2883ff58-b223-4e6e-b762-4a4033b9d109"
        },
        {
            "Command": "I want a menu for Johnny",
            "Expected": "Waiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "proper_q(x14,named(Johnny,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "168c1644-2145-497f-96ae-e60e532e771c"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "1b1095b6-9deb-4f4b-b899-086df06dd56b"
        },
        {
            "Command": "I want a menu",
            "Expected": "Waiter: Oh, I already gave you a menu. You can see that there is a menu in front of you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "88c3551b-31b7-4cc2-af25-b3f19ea5af2e"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "06f791d6-1887-422e-9c75-d121f7627dc8"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "21563f12-c971-4751-9127-fcda795ee910"
        },
        {
            "Command": "I want a table and a water",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: water is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x13,_table_n_1(x13),_a_q(x18,_water_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "c88fe13b-4291-4f37-a0fd-1658cb18c699"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a water for you.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "bd61f363-db82-4c08-931a-8b6dbf48a623"
        },
        {
            "Command": "no",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "d10b2fbf-eb59-4ce7-ba36-f82fc3d0fef8"
        }
    ],
    "ElapsedTime": 7.40405
}