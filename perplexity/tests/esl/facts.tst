{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b337f508-a5fc-4bdf-aaed-84e701c86181"
        },
        {
            "Command": "want food",
            "Expected": "I do not want food\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_food_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c3d69e0c-a5dd-4900-9ec4-17817e5f4fda"
        },
        {
            "Command": "salad is a vegetarian meal",
            "Expected": "Yes, that is true.\nHost: How can I help you today?",
            "Tree": "udef_q(x3,_salad_n_1(x3),_a_q(x8,[_dish_n_of(x8), _vegetarian_a_1(e13,x8)],_be_v_id(e2,x3,x8)))",
            "Enabled": true,
            "ID": "261277f2-240f-44f9-ad6d-3b0eda027319"
        },
        {
            "Command": "We are hungry!",
            "Expected": "Ahh. I did not know that!\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_hungry_a_1(e2,x3))",
            "Enabled": true,
            "ID": "4547bbc7-098c-4b9e-9220-0e06685bb46f"
        },
        {
            "Command": "I am skinny",
            "Expected": "Ahh. I did not know that!\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_skinny_a_1(e2,x3))",
            "Enabled": true,
            "ID": "f9b3a4e6-9ee8-4c5f-a427-abb6e48c4d85"
        }
    ],
    "ElapsedTime": 23.83734
}