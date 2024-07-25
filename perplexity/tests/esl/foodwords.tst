{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "I want tea",
            "Expected": "I'm sorry, we don't serve that here. Get the menu to see what is available.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_tea_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f16594d-476c-4026-b82c-ea859bf4a489"
        },
        {
            "Command": "I want a burger",
            "Expected": "I'm sorry, we don't serve that here. Get the menu to see what is available.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_burger_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "84e97d62-1194-45c1-ade3-35bbbdf85736"
        },
        {
            "Command": "I want a tablecloth",
            "Expected": "I don't know the words: tablecloth",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_tablecloth_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "79268d62-547f-4085-8263-639aee0b52fd"
        },
        {
            "Command": "Do you have tea?",
            "Expected": "I'm sorry, we don't serve that here. Get the menu to see what is available.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_tea_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a3841484-fb33-4893-9ae9-0959e1e69ba2"
        },
        {
            "Command": "Do you have a mouse?",
            "Expected": "I'm sorry, I'm not sure if we have that.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_mouse_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ec808d20-3891-4440-aaa4-84ce92dfdc27"
        },
        {
            "Command": "tea",
            "Expected": "Host: I'm sorry, we don't serve that here. Get the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x4,_tea_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "e1a2d88b-6308-4888-93d1-32d59f2f114d"
        },
        {
            "Command": "mouse",
            "Expected": "Host: Sorry, I don't think we have that here.\nHost: How can I help you today?",
            "Tree": "udef_q(x4,_mouse_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "f0d534fd-51be-4227-a571-0380025a04af"
        }
    ],
    "ElapsedTime": 7.70442
}