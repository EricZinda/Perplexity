{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "f3a009dc-1a2d-4a79-ac60-805972e7873f"
        },
        {
            "Command": "how much is soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),udef_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "4adb123a-f0a5-47fc-8eb5-a58cf4a9cd81"
        },
        {
            "Command": "my son and I want soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for Johnny and a soup for you?",
            "Tree": "pronoun_q(x13,pron(x13),pronoun_q(x20,pron(x20),udef_q(x25,_soup_n_1(x25),udef_q(x3,def_explicit_q(x8,[_son_n_of(x8,i18), poss(e12,x8,x13)],_and_c(x3,x8,x20)),_want_v_1(e2,x3,x25)))))",
            "Enabled": true,
            "ID": "f818e092-d5e9-4c93-8df6-4aa33ea933ca"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a soup for Johnny.\nWaiter: Here is a soup for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "dd9e2da0-7e00-4c07-aed9-92117eea2446"
        }
    ],
    "ElapsedTime": 2.742
}