{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "is the soup vegetarian?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_soup_n_1(x3),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "5f6ab01b-f45d-45e0-80e5-2f73e4387ece"
        },
        {
            "Command": "is the soup not vegetarian?",
            "Expected": "That isn't true, there isn't the soup that isn't the vegetarian soup",
            "Tree": "neg(e8,_the_q(x3,_soup_n_1(x3),_vegetarian_a_1(e2,x3)))",
            "Enabled": false,
            "ID": "26fc6f0a-7692-4135-8859-c27a1b3e9129"
        }
    ]
}