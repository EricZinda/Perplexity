{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "I'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b03ec48e-4546-4414-b5c3-cb9458e38709"
        },
        {
            "Command": "I'd like a salmon'",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_salmon_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "6dc5aeff-5095-436f-923f-b814daf709be"
        },
        {
            "Command": "I'd like a soup'",
            "Expected": "Son: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "9ec2db5e-4c9c-4fb2-8fb8-2ef9a00e2f55"
        },
        {
            "Command": "Do you have a bill?",
            "Expected": "Waiter: Let's finish up this order before we get your bill.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_bill_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1092aa0b-f721-4a0b-9e5c-e8ff7e3312f7"
        },
        {
            "Command": "I'd like the bill'",
            "Expected": "Waiter: Let's finish up this order before we get your bill.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i16),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ff902a95-c906-4c0f-991b-82e6a6fc54be"
        },
        {
            "Command": "Can I have the bill",
            "Expected": "Waiter: Let's finish up this order before we get your bill.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i16),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "76892157-de31-423b-9717-632e623b2316"
        },
        {
            "Command": "can we please have the check?",
            "Expected": "Waiter: Let's finish up this order before we get your bill.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x12,_check_n_of(x12,i17),pronoun_q(x3,pron(x3),[_please_a_1(e10,e11), event_replace(u99,e2,e11), _have_v_1_able(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "6ae8c19c-ba52-4a47-98f5-890110bd8e01"
        },
        {
            "Command": "could we please have the check?",
            "Expected": "Waiter: Let's finish up this order before we get your bill.\nWaiter: Can I get you anything else?",
            "Tree": "_the_q(x12,_check_n_of(x12,i17),pronoun_q(x3,pron(x3),[_please_a_1(e10,e11), event_replace(u99,e2,e11), _have_v_1_able(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "827e8da2-0cab-4d3d-9c61-5909d5221959"
        }
    ],
    "ElapsedTime": 3.71542
}