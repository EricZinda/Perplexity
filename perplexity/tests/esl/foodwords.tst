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
        }
    ],
    "ElapsedTime": 7.70442
}