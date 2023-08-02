{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "seat me",
            "Expected": "How many in your party?",
            "Tree": "pronoun_q(x8,pron(x8),pronoun_q(x3,pron(x3),_seat_v_cause(e2,x3,x8)))",
            "Enabled": true,
            "ID": "307e0d6e-23a7-4890-9a1e-9a87858cd12a"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x4,card(2,x4,i10),unknown(e2,x4))",
            "Enabled": true,
            "ID": "498228e6-97a5-4704-8e7b-1c9b3c6e40db"
        }
    ]
}