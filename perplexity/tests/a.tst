{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f72f1ef1-1390-4f34-aa6e-e1b0670d845d"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "cc4b5317-5f26-491b-aabb-c7784804a6ab"
        },
        {
            "Command": "how much are the soup and salad?",
            "Expected": "4 dollars\n3 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,udef_q(x20,_soup_n_1(x20),udef_q(x25,_salad_n_1(x25),_and_c(x3,x20,x25))),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "27506662-fd0f-4daa-bcc2-1fbba68ea9e7"
        }
    ]
}