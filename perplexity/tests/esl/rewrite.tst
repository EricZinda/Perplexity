{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5c0b3d20-fa58-4cf1-b9be-1c410f699704"
        },
        {
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "9f7092e1-f583-4537-a746-5276804ae76a"
        },
        {
            "Command": "Do I have a son?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_son_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f8fa4a7-85dd-4be5-a9fe-e0ee0cfe1e43"
        },
        {
            "Command": "Do you have a steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "805b7349-7c9a-4e6f-af21-c51e1ef16da5"
        },
        {
            "Command": "Do you have the steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "96fa2577-6b6e-489e-9139-d68dc0ee0c32"
        },
        {
            "Command": "Do you have the table?",
            "Expected": "I'm not sure which table you mean.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5228b43a-2306-4599-9955-09dbb3a7b2c1"
        }
    ]
}