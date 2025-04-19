{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/runfunction samples.solver_tests.solver_tests, one_predication_zero_disjunction_fails",
            "Expected": "Interpretation: -1@0\n-1@0 interpretation has error: ['errorText', 'Test']\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "f4eb4bce-d0a5-4cca-95d7-2b3e2797d1e1"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,one_predication_zero_disjunction_success",
            "Expected": "Interpretation: -1@0\ntree_lineage=('-1@0',), x1=('disjunction_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='zero_disjunction_success', extra_arg=None, id=127)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "ebf8b564-6b1c-43c9-aebc-31e588b337b2"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,one_predication_one_disjunction_success",
            "Expected": "Interpretation: -1@0.0@1\ntree_lineage=('-1@0.0@1',), x1=('disjunction_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='one_disjunction_success', extra_arg=None, id=132)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "00025408-a600-411b-b64d-b50509aaee7c"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,one_predication_two_disjunction_success",
            "Expected": "Interpretation: -1@0.0@1\ntree_lineage=('-1@0.0@1',), x1=('disjunction_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='two_disjunctions_success', extra_arg=None, id=137)},)\nInterpretation: -1@0.0@2\ntree_lineage=('-1@0.0@2',), x1=('disjunction_2',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='two_disjunctions_success', extra_arg=None, id=137)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "7dbabdd8-a19a-4057-a8a6-72187932f717"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,one_predication_two_disjunction_success_fail",
            "Expected": "Interpretation: -1@0.0@1\ntree_lineage=('-1@0.0@1',), x1=('disjunction_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='two_disjunctions_success_fail', extra_arg=None, id=142)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "a0db6850-f686-4407-aea9-3cd1439c3d31"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,pred1_succ_pred2_succconj_succconj",
            "Expected": "Interpretation: -1@0.1@1\ntree_lineage=('-1@0.1@1',), x1=('predication1_1',), x2=('predication2_1_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication1', extra_arg=None, id=147), 1: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication2', extra_arg=None, id=152)},)\nInterpretation: -1@0.1@2\ntree_lineage=('-1@0.1@2',), x1=('predication1_1',), x2=('predication2_2_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication1', extra_arg=None, id=147), 1: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication2', extra_arg=None, id=152)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "7cc3d087-585d-4fec-9145-101902647ec8"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,pred1_p11cs_p12cs_pred2_p11cf_p12cs",
            "Expected": "Interpretation: -1@0.0@1\n-1@0.0@1 interpretation has error: ['predication2', 'Fail', \"x1=('predication1_1',)\"]\nInterpretation: -1@0.0@2.1@1\ntree_lineage=('-1@0.0@2.1@1',), x1=('predication1_2',), x2=('predication2_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication1', extra_arg=None, id=147), 1: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication2', extra_arg=None, id=152)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "669e96ca-1a46-44ef-8e00-48bda8e127de"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,pred1_succconj_succconj_pred2_fail",
            "Expected": "Interpretation: -1@0.0@1\n-1@0.0@1 interpretation has error: ['predication2', 'Fail', \"x1=('predication1_1',)\"]\nInterpretation: -1@0.0@2\n-1@0.0@2 interpretation has error: ['predication2', 'Fail', \"x1=('predication1_2',)\"]\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "a4bd3412-89ef-4426-918c-7c574a273deb"
        },
        {
            "Command": "/runfunction samples.solver_tests.solver_tests,p11c_p12c__p11_p21_p12_p22__p11_p21_p31c_p12_p22_p32c",
            "Expected": "Interpretation: -1@0.0@1.2@1\ntree_lineage=('-1@0.0@1.2@1',), x1=('predication1_1',), x2=('predication2_1',), x3=('predication3_1',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication1', extra_arg=None, id=147), 1: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication2', extra_arg=None, id=152), 2: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication3', extra_arg=None, id=157)},)\nInterpretation: -1@0.0@2.2@2\ntree_lineage=('-1@0.0@2.2@2',), x1=('predication1_2',), x2=('predication2_2',), x3=('predication3_2',), interpretation=({0: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication1', extra_arg=None, id=147), 1: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication2', extra_arg=None, id=152), 2: VocabularyEntry(module='samples.solver_tests.solver_tests', function='predication3', extra_arg=None, id=157)},)\n",
            "Tree": "None",
            "Enabled": true,
            "ID": "4f4e2cf0-3ca1-46e8-8727-873c8505572b"
        }
    ],
    "ElapsedTime": 5.51334
}