{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "69c95107-36db-4bca-b2b2-ee7d0a2a1a0e"
        },
        {
            "Command": "Could i have a table for two please.",
            "Expected": "Sorry, could you rephrase that?\nHost: How can I help you today?",
            "Tree": "None",
            "Enabled": true,
            "ID": "1bab67c2-65c4-47f9-8ad9-8b5b7747be02"
        },
        {
            "Command": "eat now",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "def_implicit_q(x10,[time_n(x10), _now_a_1(e15,x10)],pronoun_q(x3,pron(x3),[loc_nonsp(e9,e2,x10), _eat_v_1(e2,x3,i8)]))",
            "Enabled": true,
            "ID": "cabcc762-37f2-4e67-a738-bb0d3120727b"
        },
        {
            "Command": "I would like to order vegetarian dish",
            "Expected": "Sorry, could you rephrase that?\nHost: How can I help you today?",
            "Tree": "None",
            "Enabled": true,
            "ID": "097e4840-26ab-4e7d-8bf1-88892812a855"
        },
        {
            "Command": "leving",
            "Expected": "I don't know the words: leving\nHost: How can I help you today?",
            "Tree": "None",
            "Enabled": true,
            "ID": "034639aa-773d-4d01-8d2d-cf1f8ace15b8"
        },
        {
            "Command": "I'll have the chicken and my son will have the soup and the salad",
            "Expected": "That was too complicated for me to understand ...\nHost: How can I help you today?",
            "Tree": "None",
            "Enabled": true,
            "ID": "eede2168-d1a4-4c4b-af7a-d3aa58ddc989"
        },
        {
            "Command": "I want an order of the table",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "_the_q(x13,_table_n_1(x13),pronoun_q(x3,pron(x3),_a_q(x8,_order_n_of(x8,x13),_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "410c600c-dc36-4030-bab1-27896a1acf0e"
        },
        {
            "Command": "Can I take a table?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _take_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "82b6ed9b-e700-48e9-bee5-0e0cf89f89cf"
        },
        {
            "Command": "Can you take a table?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _take_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "aad1420f-f6b6-4e90-8a3d-301e7b516689"
        },
        {
            "Command": "we take menus",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_menu_n_1(x8),_take_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "445119ea-e0c7-4661-8b74-003da5a16493"
        },
        {
            "Command": "I will see a table",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8e88c9b7-8751-4487-a4b9-4f4e45086a34"
        },
        {
            "Command": "I will see a menu?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e50a9ff9-e8f1-4d19-a266-beec60e424cd"
        },
        {
            "Command": "What do I see?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_see_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "4e6877f3-7f0a-45a5-8c32-ebb9b3c22758"
        },
        {
            "Command": "Who sees a menu?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c04dda2f-2d31-40a8-879a-4ea629230615"
        },
        {
            "Command": "I see a menu?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "81732fad-fa6f-4455-b39c-cc10c68c2d98"
        },
        {
            "Command": "I see a menu.",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "079692bf-637e-4243-a496-1b8ef6a98d49"
        },
        {
            "Command": "I can see a menu",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _see_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "ad7a32a4-cce3-4517-a576-3796abdb839c"
        },
        {
            "Command": "I sit down",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "0fa04472-445c-481c-b247-6749f5cc46d5"
        },
        {
            "Command": "I can sit down",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _sit_v_down_able(e2,x3)])",
            "Enabled": true,
            "ID": "76780ce0-5445-401f-85d5-aac3fba9bd12"
        },
        {
            "Command": "I can sit",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _sit_v_1_able(e2,x3)])",
            "Enabled": true,
            "ID": "9295777f-f7fe-4346-93d3-217accf792bb"
        },
        {
            "Command": "Who sits down?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "b625ae45-b225-479c-b46c-e0f75f2a7dfe"
        },
        {
            "Command": "Who is sitting down?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "008b37e8-f81e-41f3-bb3a-e1ecc88c1208"
        },
        {
            "Command": "Who sits down?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "91f5c871-4e97-4b6a-9161-6b62878abd8f"
        },
        {
            "Command": "Who will sit down?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "which_q(x3,person(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "2c790d66-95f5-4e20-a8ef-70c01b0725cb"
        },
        {
            "Command": "You will sit down",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "5138ec3b-eea1-4369-995d-3a7aa16d4194"
        },
        {
            "Command": "Will I sit down?",
            "Expected": "I'm not sure what that means.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_sit_v_down(e2,x3))",
            "Enabled": true,
            "ID": "ed1aa6a9-6682-4412-9960-b5c1b570163f"
        }
    ],
    "ElapsedTime": 39.32691
}