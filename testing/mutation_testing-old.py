import random
from copy import deepcopy
from common.TimedWord import TimedWord
from common.hypothesis import OTATran, MutationState
from common.TimeInterval import guard_split
from testing.random_testing import test_generation_4


class NFA(object):
    def __init__(self, states, init_state, actions, trans, sink_state, final_states):
        self.states = states
        self.init_state = init_state
        self.actions = actions
        self.trans = trans
        self.sink_state = sink_state
        self.final_states = final_states  # timed中为接受状态集合，state中为更改接受性的最终状态


# 基于变异的测试主函数
def mutation_testing(hypothesisOTA, upper_guard, state_num, pre_ctx, system):
    equivalent = True
    ctx = None

    # 参数配置 - 测试生成
    pstart = 0.4
    pstop = 0.05
    pvalid = 0.8
    pnext = 0.8
    max_steps = min(int(2 * state_num), int(2 * len(hypothesisOTA.states)))
    test_num = int(len(hypothesisOTA.states) * len(hypothesisOTA.actions) * upper_guard * 10)

    State = []
    state_time = 0
    for state in hypothesisOTA.states:
        State.append(MutationState(state, 0))
    for tran in hypothesisOTA.trans:
        State[tran.target].in_degree += 1

    # 参数配置 - 变异相关
    duration = system.get_minimal_duration()  # It can also be set by the user.
    if duration < 1:
        duration = 1
    nacc = 8
    k = 1

    # 测试集生成
    tests = []
    for i in range(test_num):
        test, State = test_generation_4(hypothesisOTA, pstart, pstop, pvalid, pnext, max_steps, upper_guard, pre_ctx, State)
        tests.append(test)
        state_time += len(test.time_words) + 1
    for state in hypothesisOTA.states:
        State[state].reach_rate = 1 - State[state].reach_time / state_time

    tested = []  # 缓存已测试序列

    # step1: timed变异
    timed_tests = mutation_timed(hypothesisOTA, duration, upper_guard, tests, State)
    if len(timed_tests) > 0:
        print('number of timed tests', len(timed_tests))
        equivalent, ctx = test_execution(hypothesisOTA, system, timed_tests)
        tested = timed_tests

    # step2: 如果未找到反例, state变异    
    if equivalent:
        state_tests = mutation_state(hypothesisOTA, state_num, nacc, k, tests, State)
        if len(state_tests) > 0:
            state_tests = remove_tested(state_tests, tested)
            print('number of state tests', len(state_tests))
            equivalent, ctx = test_execution(hypothesisOTA, system, state_tests)
            tested += state_tests

    '''
    timed_tests = mutation_timed(hypothesisOTA, duration, upper_guard, tests)
    if len(timed_tests) > 0:
        print('number of timed tests', len(timed_tests))
        equivalent, ctx = test_execution(hypothesisOTA, system, timed_tests)
        tested = timed_tests

    state_tests = mutation_state(hypothesisOTA, state_num, nacc, k, tests)
    if len(state_tests) > 0:
        state_tests = remove_tested(state_tests, tested)
        print('number of state tests', len(state_tests))
        equivalent, ctx = test_execution(hypothesisOTA, system, state_tests)
        tested += state_tests
    '''

    # # step3: 随机选取测试集直到数量满足nsel
    # if equivalent and len(timed_tests) + len(state_tests) < nsel:
    #     tests = remove_tested(tests, tested)
    #     if nsel - len(timed_tests) - len(state_tests) > len(tests):
    #         random_tests = tests
    #     else:
    #         random_tests = random.sample(tests, nsel - len(timed_tests) - len(state_tests))
    #     print('number of random tests', len(random_tests))
    #     equivalent, ctx = test_execution(hypothesisOTA, system, random_tests)

    return equivalent, ctx


# timed mutation
def mutation_timed(hypothesis, duration, upper_guard, tests, State):
    Tsel = []
    # 生成变异体
    mutants = timed_mutation_generation(hypothesis, duration, upper_guard)  # 这里的mutants是trans信息
    print('number of timed_mutations', len(mutants))
    # 生成NFA
    muts_NFA = timed_NFA_generation(mutants, hypothesis)
    print('number of timed NFA trans', len(muts_NFA.trans))
    # 变异分析
    print('Starting mutation analysis...')
    tran_dict = get_tran_dict(muts_NFA)
    tests_valid = []
    C = []
    C_tests = []
    max_mutWeight = 0
    # max_stateWeight = 0
    max_lenWeight = 0
    min_mutWeight = float('inf')
    # min_stateWeight = float('inf')
    min_lenWeight = float('inf')
    for test in tests:
        C_test, C, test = timed_mutation_analysis(muts_NFA, hypothesis, test, C, tran_dict, State, len(mutants))
        if C_test:
            tests_valid.append(test)
            C_tests.append(C_test)

            if len(C_test) > max_mutWeight:
                max_mutWeight = len(C_test)
            # if test.state_weight > max_stateWeight:
            #    max_stateWeight = test.state_weight
            if test.length > max_lenWeight:
                max_lenWeight = test.length
            if len(C_test) < min_mutWeight:
                min_mutWeight = len(C_test)
            # if test.state_weight < min_stateWeight:
            #    min_stateWeight = test.state_weight
            if test.length < min_lenWeight:
                min_lenWeight = test.length
    if C:
        coverage = float(len(C)) / float(len(mutants))
        print("timed mutation coverage:", coverage)

    # test属性归一化
    tests_valid = rerange_test(tests_valid, C_tests, max_mutWeight, max_lenWeight, min_mutWeight, min_lenWeight)
    # 测试筛选
    if C_tests:
        # Tsel = test_selection(tests_valid, C, C_tests)
        Tsel = test_selection_new(tests_valid, C, C_tests)
    return Tsel


# timed mutation generation/operator
def timed_mutation_generation(hypothesis, duration, upper_guard):
    mutations = []
    mut_num = 0
    for tran in hypothesis.trans:
        if tran.source == hypothesis.sink_state and tran.target == hypothesis.sink_state:
            continue
        trans = split_tran_guard(tran, duration, upper_guard)
        for state in hypothesis.states:
            if state != tran.target:
                for prefix in trans:
                    temp = deepcopy(prefix)
                    temp.target = state
                    temp.tran_id = 'tran' + str(mut_num)
                    mut_num += 1
                    mutations.append(temp)
            else:
                temp = deepcopy(tran)
                temp.reset = not tran.reset
                temp.tran_id = 'tran' + str(mut_num)
                mut_num += 1
                mutations.append(temp)
    return mutations


# 生成 timed_mutant_NFA 结构
def timed_NFA_generation(mutants, hypothesis):
    hypothesis = deepcopy(hypothesis)
    trans = hypothesis.trans
    trans.extend(mutants)
    return NFA(hypothesis.states, hypothesis.init_state, hypothesis.actions, trans, hypothesis.sink_state, hypothesis.accept_states)


# timed 变异分析
def timed_mutation_analysis(muts_NFA, hypothesis, test, C, tran_dict, State, mut_num):
    C_test = []

    # 获取test在hypothesis里的结果，用于与muts区分
    hyp_tran_dict = get_tran_dict(hypothesis)
    now_time = 0
    now_state = hypothesis.init_state
    test_result = []
    for t in test.time_words:
        temp_time = t.time + now_time
        new_LTW = TimedWord(t.action, temp_time)
        for tran in hyp_tran_dict[now_state]:
            if tran.is_passing_tran(new_LTW):
                now_state = tran.target
                if tran.reset:
                    now_time = 0
                else:
                    now_time = temp_time
                if now_state in hypothesis.accept_states:
                    test_result.append(1)
                elif now_state == hypothesis.sink_state:
                    test_result.append(-1)
                else:
                    test_result.append(0)

    def tree_create(state, preTime, test_index, mut_tran):
        if test_index >= len(test.time_words):
            return True
        cur_time = test.time_words[test_index].time + preTime
        cur_LTW = TimedWord(test.time_words[test_index].action, cur_time)

        if mut_tran:
            if state == mut_tran.source and mut_tran.is_passing_tran(cur_LTW):
                if mut_tran.reset:
                    tempTime = 0
                else:
                    tempTime = cur_time
                if mut_tran.target in muts_NFA.final_states:
                    state_flag = 1
                elif mut_tran.target == muts_NFA.sink_state:
                    state_flag = -1
                else:
                    state_flag = 0
                if state_flag != test_result[test_index]:
                    if mut_tran.tran_id not in C_test:
                        C_test.append(mut_tran.tran_id)
                    if mut_tran.tran_id not in C:
                        C.append(mut_tran.tran_id)
                    return True
                tree_create(mut_tran.target, tempTime, test_index + 1, mut_tran)
                return True
            else:
                cur_trans = hyp_tran_dict[state]
        else:
            cur_trans = tran_dict[state]

        for cur_tran in cur_trans:
            if cur_tran.is_passing_tran(cur_LTW):
                if cur_tran.reset:
                    tempTime = 0
                else:
                    tempTime = cur_time
                if cur_tran.target in muts_NFA.final_states:
                    state_flag = 1
                elif cur_tran.target == muts_NFA.sink_state:
                    state_flag = -1
                else:
                    state_flag = 0

                if isinstance(cur_tran.tran_id, str):
                    mut_tran = cur_tran

                if mut_tran:
                    if state_flag != test_result[test_index]:
                        if mut_tran.tran_id not in C_test:
                            C_test.append(mut_tran.tran_id)
                        if mut_tran.tran_id not in C:
                            C.append(mut_tran.tran_id)
                        return True
                tree_create(cur_tran.target, tempTime, test_index + 1, mut_tran)

    tree_create(muts_NFA.init_state, 0, 0, None)
    # test.mut_weight = len(C_test) / mut_num
    # state_weight = 0
    # for s in test.pass_states:
    #    test.state_weight += State[s].reach_rate
    # test.weight = test.pass_mut_num / (state_weight * test.length)
    # test.weight = 10 / (state_weight * test.length)
    # test.weight = test.mut_weight*0.0 + test.state_weight * 1 + test.len_weight * 0.0
    # print(test.pass_mut_num, state_weight, test.length, test.weight)
    return C_test, C, test


# split_state mutation
def mutation_state(hypothesis, state_num, nacc, k, tests, State):
    Tsel = []
    # 生成变异体
    mutants = split_state_mutation_generation(hypothesis, nacc, k, state_num)
    print('number of split_state_mutations', len(mutants))
    # 生成NFA
    muts_NFA = state_NFA_generation(mutants, hypothesis)
    print('number of state NFA trans', len(muts_NFA.trans))
    # 变异分析
    print('Starting mutation analysis...')
    tran_dict = get_tran_dict(muts_NFA)
    tests_valid = []
    C = []
    C_tests = []

    max_mutWeight = 0
    # max_stateWeight = 0
    max_lenWeight = 0
    min_mutWeight = float('inf')
    # min_stateWeight = float('inf')
    min_lenWeight = float('inf')
    for test in tests:
        C_test, C, test = state_mutation_analysis(muts_NFA, test, C, tran_dict, State, len(mutants))
        if C_test:
            tests_valid.append(test)
            C_tests.append(C_test)

            if len(C_test) > max_mutWeight:
                max_mutWeight = len(C_test)
            # if test.state_weight > max_stateWeight:
            #    max_stateWeight = test.state_weight
            if test.length > max_lenWeight:
                max_lenWeight = test.length
            if len(C_test) < min_mutWeight:
                min_mutWeight = len(C_test)
            # if test.state_weight < min_stateWeight:
            #    min_stateWeight = test.state_weight
            if test.length < min_lenWeight:
                min_lenWeight = test.length
    if C:
        coverage = float(len(C)) / float(len(mutants))
        print("timed mutation coverage:", coverage)

    # test属性归一化
    tests_valid = rerange_test(tests_valid, C_tests, max_mutWeight, max_lenWeight, min_mutWeight, min_lenWeight)

    # 测试筛选
    if C_tests:
        # Tsel = test_selection(tests_valid, C, C_tests)
        Tsel = test_selection_new(tests_valid, C, C_tests)
    return Tsel


# split-state mutation generation
def split_state_mutation_generation(hypothesis, nacc, k, state_num):
    temp_mutations = []
    for state in hypothesis.states:
        if state == hypothesis.sink_state:
            continue
        set_accq = get_all_acc(hypothesis, state, state_num)
        if len(set_accq) < 2:
            continue
        elif nacc >= len(set_accq):
            subset_accq = set_accq
        else:
            subset_accq = random.sample(set_accq, nacc)
        for s1 in subset_accq:
            for s2 in subset_accq:
                if s1 == s2:
                    continue
                else:
                    muts = split_state_operator(s1, s2, k, hypothesis)
                    if muts is not None:
                        temp_mutations.extend(muts)
    return temp_mutations


# 生成 state_mutant_NFA 结构
def state_NFA_generation(mutations, hypothesis):
    hypothesis = deepcopy(hypothesis)
    states = hypothesis.states
    init_state = hypothesis.init_state
    actions = hypothesis.actions
    trans = hypothesis.trans
    sink_state = hypothesis.sink_state
    final_states = []
    mId = 0
    for mutation in mutations:
        count = 0
        source_state = mutation[0].source
        target_state = None
        for tran in mutation:
            tran = deepcopy(tran)
            target_state = str(mId) + '_' + str(count)
            tran.source = source_state
            tran.target = target_state
            trans.append(tran)
            states.append(target_state)
            count += 1
            source_state = target_state
        mId += 1
        final_states.append(target_state)
    return NFA(states, init_state, actions, trans, sink_state, final_states)


# state 变异分析
def state_mutation_analysis(muts_NFA, test, C, tran_dict, State, mut_num):
    C_test = []

    def tree_create(state, preTime, test_index):
        if test_index >= len(test.time_words):
            return True
        cur_time = test.time_words[test_index].time + preTime
        new_LTW = TimedWord(test.time_words[test_index].action, cur_time)
        if state not in tran_dict.keys():
            return True
        cur_trans = tran_dict[state]
        for tran in cur_trans:
            if tran.is_passing_tran(new_LTW):
                if tran.reset:
                    tempTime = 0
                else:
                    tempTime = cur_time
                if tran.target in muts_NFA.final_states:
                    mId = tran.target.split('_')[0]
                    if mId not in C_test:
                        C_test.append(mId)
                    if mId not in C:
                        C.append(mId)
                if tran.target == muts_NFA.sink_state:
                    continue
                tree_create(tran.target, tempTime, test_index + 1)

    # tree_create(muts_NFA.init_state, 0, 0)
    # test.pass_mut_num = len(C_test) / mut_num * 0.1
    # state_weight = 0
    # for s in test.pass_states:
    #    test.state_weight += State[s].reach_rate
    # test.weight = test.pass_mut_num / (state_weight * test.length)
    # test.weight = 10 / (state_weight * test.length)
    # test.weight = test.pass_mut_num*0.0 + state_weight * 1 + test.length * 0.0
    # print(test.pass_mut_num, state_weight, test.length, test.weight)
    return C_test, C, test


# 测试筛选
def test_selection_new(Tests, C, C_tests):
    Tsel = []
    Cover_test = {}
    tests = deepcopy(Tests)
    cset = deepcopy(C_tests)

    for mut in C:
        Cover_test[mut] = []
        for i in range(len(tests)):
            if mut in cset[i]:
                Cover_test[mut].append((i, tests[i], tests[i].weight))  # 能够覆盖当前mutation的test的index
        # Cover_test[mut].sort(reverse=True)
        Cover_test[mut] = sorted(Cover_test[mut], key=lambda x: x[2], reverse=True)
        Cover_test[mut].append(len(Cover_test[mut]))
        # print(Cover_test[mut])
    # print(Cover_test)
    Cover_test_sort = sorted(Cover_test.items(), key=lambda d: d[1][-1])
    # print(Cover_test_sort)

    for ctest in Cover_test_sort:
        # print(ctest)
        if not Cover_test.get(ctest[0]):
            continue
        for test in Cover_test[ctest[0]]:
            if test[1] not in Tsel:
                Tsel.append(test[1])
                break
        for mut in cset[int(test[0])]:
            if not Cover_test.get(mut):
                continue
            del (Cover_test[mut])
    return Tsel


def test_selection(Tests, C, C_tests):
    Tsel = []
    c = deepcopy(C)  # all mutations
    tests = deepcopy(Tests)  # tests
    cset = deepcopy(C_tests)  # tests 对应的 cover mutation set
    pre_set = []
    while c:
        cur_index = 0
        cur_max = []
        for i in range(len(cset)):
            cset[i] = list(set(cset[i]).difference(set(pre_set)))
            if len(cur_max) < len(cset[i]):
                cur_max = cset[i]
                cur_index = i
        if cur_max:
            Tsel.append(tests[cur_index])
            pre_set = cur_max
        else:
            break
    return Tsel


# 测试执行
def test_execution(hypothesis, system, tests):
    flag = True
    ctx = []
    for test in tests:
        DRTWs, value = hypothesis.test_DTWs(test.time_words)
        realDRTWs, realValue = system.test_DTWs(test.time_words)
        if realValue != value:
            flag = False
            ctx = test.time_words
            return flag, ctx
    return flag, ctx


# --------------------------------- auxiliary function --------------------------------

# tests中删除cur_tests
def remove_tested(tests, cur_tests):
    for test in cur_tests:
        if test in tests:
            tests.remove(test)
    return tests


# 将NFA中的迁移按source分组
def get_tran_dict(muts_NFA):
    tran_dict = {}
    for tran in muts_NFA.trans:
        if tran.source in tran_dict.keys():
            tran_dict[tran.source].append(tran)
        else:
            tran_dict[tran.source] = [tran]
    return tran_dict


# 将迁移的guard分割
def split_tran_guard(tran, region_num, upper_guard):
    trans = []
    for guard in tran.guards:
        temp_guards = guard_split(guard, region_num, upper_guard)
        if not temp_guards:
            trans.append(OTATran('', tran.source, tran.action, [guard], tran.reset, tran.target))
            trans.append(OTATran('', tran.source, tran.action, [guard], not tran.reset, tran.target))
        for temp_guard in temp_guards:
            trans.append(OTATran('', tran.source, tran.action, [temp_guard], tran.reset, tran.target))
            trans.append(OTATran('', tran.source, tran.action, [temp_guard], not tran.reset, tran.target))
    return trans


# split-state operator
def split_state_operator(s1, s2, k, hypothesis):
    if not s1:
        suffix = []
        p_tran = OTATran('', hypothesis.init_state, None, None, True, hypothesis.init_state)
        temp_state = hypothesis.init_state
    else:
        suffix = arg_maxs(s1, s2)
        prefix = s1[0:len(s1) - len(suffix)]
        temp_state = s1[-1].target
        if len(prefix) == 0:
            p_tran = OTATran('', hypothesis.init_state, None, None, True, hypothesis.init_state)
        else:
            p_tran = prefix[len(prefix) - 1]
    mutants = []
    trans_list = k_step_trans(hypothesis, temp_state, k)
    for distSeq in trans_list:
        mut_tran = [p_tran] + suffix + distSeq
        mutants.append(mut_tran)
    return mutants


# get mutated access seq leading to a single state
def get_all_acc(hypothesis, state, state_num):
    paths = []
    max_path_length = min(int(len(hypothesis.states) * 1.5), state_num * 1.5)

    if state == hypothesis.init_state:
        paths.append([])

    def get_next_tran(sn, path):
        if len(path) > max_path_length or sn == hypothesis.sink_state:
            return True
        if sn == state and path:
            if path not in paths:
                paths.append(path)
        for tran in hypothesis.trans:
            if tran.source == sn:
                if len(path) > 0 and tran == path[-1]:
                    continue
                get_next_tran(tran.target, deepcopy(path) + [tran])

    get_next_tran(hypothesis.init_state, [])
    return paths


# 找到s1和s2的最长公共后缀
def arg_maxs(s1, s2):
    ts = []
    if len(s1) < len(s2):
        min_test = s1
    else:
        min_test = s2
    for i in range(len(min_test)):
        if not s1[-1 - i].tran_id == s2[-1 - i].tran_id:
            break
        ts = min_test[(len(min_test) - 1 - i):]
    return ts


# 找到qs状态后走step的所有路径
def k_step_trans(hypothesis, q, k):
    trans_list = []

    def recursion(cur_state, paths):
        if len(paths) == k:
            if paths not in trans_list:
                trans_list.append(paths)
            return True
        for tran in hypothesis.trans:
            if tran.source == cur_state:
                if len(paths) > 0 and paths[-1] == tran:
                    continue
                recursion(tran.target, deepcopy(paths) + [tran])

    recursion(q, [])
    return trans_list


def rerange_test(tests_valid, C_tests, max_mutWeight, max_lenWeight, min_mutWeight, min_lenWeight):
    index = 0
    mut_range = max_mutWeight - min_mutWeight
    # state_range = max_stateWeight - min_stateWeight
    len_range = max_lenWeight - min_lenWeight
    for test in tests_valid:
        if mut_range == 0:
            test.mut_weight = 0
        else:
            test.mut_weight = (len(C_tests[index]) - min_mutWeight) / mut_range
        # print(len(C_tests[index]), test.state_weight, test.length, test.weight)
        # test.state_weight = 1 - (test.state_weight - min_stateWeight)/state_range
        test.len_weight = 1 - (test.length - min_lenWeight) / len_range
        test.weight = 0.2 * test.mut_weight + 0.8 * test.len_weight
        # print(test.mut_weight, test.state_weight, test.len_weight, test.weight)
    return tests_valid