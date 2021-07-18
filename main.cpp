#include <iostream>
#include <vector>
#include <set>
#include <list>
#include <iterator>
#include <fstream>

using namespace std;

struct Move {
    int v;
    int Scv;
    int Stv;
};

vector<vector<double>> dist;
vector<int> I;
vector<vector<double>> sum_edges;
list<Move> tabu_list;
set<int> tabu_set;
int n, k, seconds;
const double eps = 1e-7;
auto gg = clock();
int cnt_o1 = 0;


Move O1(vector<int>& partition) {  // v: Scv -> S_tv
    cout << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    /*cout << "---------------\n";
    for (int i : partition) {
        cout << i << " ";
    }
    cout << "\n";
    for (int i = 0; i < k; ++i) {
        cout << "\n";
        for (int j = 0; j < n; ++j) {
            cout << sum_edges[i][j] << " ";
        }
    }
    cout << "---------------\n";*/
    ++cnt_o1;
    int maxv = 0, maxStv = partition[0];
    double maxgain = 0;
    for (int v = 0; v < n; ++v) {
        int Scv = partition[v];
        for (int Stv = 0; Stv < k; ++Stv) {
            if (Stv == Scv) continue;
            double g = sum_edges[Scv][v] - sum_edges[Stv][v];
            //cout << "o1 " << v << " " << Stv << " " << g << "\n";
            if (g > maxgain) {
                maxv = v;
                maxStv = Stv;
                maxgain = g;
            }
        }
    }
    int Scv = partition[maxv];
    Move move = {maxv, Scv, maxStv};
    //cout << maxv << " " << Scv << " " << maxStv << " " << maxgain << "\n";
    return move;
}

int dt(int v, int u, int Scv, int Stv, int Scu, int Stu) {
    // cout << v << " " << u << " " << Scv << " "<< Stv << " "<< Scu << " "<< Stu << "\n";
    double ans = (sum_edges[Scv][v] - sum_edges[Stv][v]) + (sum_edges[Scu][u] - sum_edges[Stu][u]);
    if (Scu == Scv && Stu == Stv) return ans + (-2) * dist[u][v];
    if (Stu == Scv && Scu == Stv) return ans + 2 * dist[u][v];
    if (Scu == Scv && Stu != Stv) return ans + (-1) * dist[u][v];
    if (Scu == Stv && Stu != Scv) return ans + 1 * dist[u][v];
    if (Scu != Scv && Stu == Stv) return ans + (-1) * dist[u][v];
    if (Scu != Stv && Stu == Scv) return ans + 1 * dist[u][v];
    return ans;
}

pair<Move, Move> O2(vector<int>& partition) {  // n: Scv -> S_tv
    //cout << "o2 " << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    pair<Move, Move> best_pair;
    double best_gain = 0;
    int v, u, Scv, Scu;
    double gain;
    for (v = 0; v < n; ++v) {
        for (u = 0; u < n; ++u) {
            if (v == u) continue;
            Scv = partition[v];
            Scu = partition[u];
            if (Scu == Scv) {
                for (int St = 0; St < k; ++St) {
                    if (St == Scu) continue;
                    gain = dt(v, u, Scv, St, Scu, St);
                    if (gain > best_gain) {
                        best_gain = gain;
                        best_pair = {{v, partition[v], St}, {u, partition[u], St}};
                    }
                }
            } else {
                for (int Stv = 0; Stv < k; ++Stv) {
                    if (Stv == Scv) continue;
                    for (int Stu = 0; Stu < k; ++Stu) {
                        if (Stu == Scu) continue;
                        gain = dt(v, u, Scv, Stv, Scu, Stu);
                        if (gain > best_gain) {
                            best_gain = gain;
                            best_pair = {{v, partition[v], Stv}, {u, partition[u], Stu}};
                        }
                    }
                }
            }
        }
    }
    //cout << "O2 "; cout << v << " " << u << "\n";
    //cout << "end of o2 " << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    if (best_gain == 0) return {{0, partition[0], partition[0]},
                                {0, partition[0], partition[0]}};
    return best_pair;
}

bool Check_if_banned(int v, int Stv, int lambda) {
    if (tabu_set.count(v) != 0) {
        return false;
    }
    auto ptr = tabu_list.end();
    --ptr;
    bool found = false;
    for (int i = 0; i < lambda; ++i) {
        auto mv = *ptr;
        if (mv.v == v && mv.Stv == Stv) {
            found = true;
            break;
        }
        if (ptr == tabu_list.begin()) break;
        --ptr;
    }
    return found;
}

Move O3(vector<int>& partition, int lambda) {  // n: Scv -> S_tv
    // int mxgain = - 1;
    cout << "o3 " << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    int maxv = 0, maxStv = partition[0], cnt = 0;
    double  maxgain = 0;
    while (maxgain < eps && cnt < (n + 1) * k) {
        ++cnt;
        for (int v = 0; v < n; ++v) {
            int Scv = partition[v];
            for (int Stv = 0; Stv < k; ++Stv) {
                double g = sum_edges[Scv][v] - sum_edges[Stv][v];
                if (!Check_if_banned(v, Stv, lambda) && g > maxgain) {
                    maxv = v;
                    maxStv = Stv;
                    maxgain = g;
                }
            }
        }
    }
    int Scv = partition[maxv];
    Move move = {maxv, Scv, maxStv};
    return move;
}

pair<Move, Move> O4(vector<int>& partition) {
    int v = 0, u = 0, Scv = partition[v], Scu = partition[u];
    int Stv = Scv, Stu = Scu;
    Move move1 = {v, Scv, Stv}, move2 = {u, Scu, Stu};

    int maxgain = 0, cnt = 0;
    while (maxgain < eps && cnt < n * k) {
        ++cnt;
        int Stv = rand() % k;
        int Stu = rand() % k;
        for (v = 0; v < n; ++v) {
            Scv = partition[v];
            if (Scv == Stv) continue;
            for (u = 0; u < n; ++u) {
                Scu = partition[u];
                if (Scu == Stu) continue;
                int d = dt(v, u, Scv, Stv, Scu, Stu);
                if (d > maxgain) {
                    maxgain = d;
                    move1 = {v, Scv, Stv};
                    move2 = {u, Scu, Stu};
                }
            }
        }
    }
    return {move1, move2};
}

Move O5(vector<int>& partition) {  // n: Scv -> S_tv
    cout << "o5 " << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    int v = rand() % n, Stv = rand() % k;
    int cnt = 0;
    while (Stv == partition[v] && cnt < n * k * 2) {
        v = rand() % n;
        Stv = rand() % k;
        ++cnt;
    }
    int Scv = partition[v];
    Move move = {v, Scv, Stv};
    cout << "end of o5 " << (clock() - gg) / CLOCKS_PER_SEC << "\n";
    return move;
}


double Update_weight(double weight, Move move) { // (n: Scv -> S_tv)
    int Scv = move.Scv, Stv = move.Stv, v = move.v;
    // return weight + gains[Stv][v];
    return weight + sum_edges[Scv][v] - sum_edges[Stv][v];
}

vector<int> Update_partition(vector<int> partition, Move move) { // (n: Scv -> S_tv)
    int Stv = move.Stv, v = move.v;
    partition[v] = Stv;
    return partition;
}

void Update_tabu(int lambda, Move move) {
    tabu_list.push_back(move);
    while (tabu_list.size() > n / 3) {
        tabu_set.erase(tabu_list.front().v);
        tabu_list.pop_front();
    }
}

void move_to_empty(vector<int>& partition, vector<int>& more_than_one, int to, vector<int>& coalition_size) {
    auto from = more_than_one.size() - 1;
    int ind = rand() % more_than_one.size();
    for (int i = 0; i < n; ++i) {
        ind += 1;
        ind %= n;
        if (partition[ind] == from) partition[ind] = to;
        coalition_size[from]--;
        coalition_size[to]++;
        if (coalition_size[from] == 0) more_than_one.pop_back();
        break;
    }
}

double f(vector<int>& partition) {
    double ans = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (partition[i] != partition[j]) ans += dist[i][j];
        }
    }
    return ans;
}

vector<int> Generate_initial_partition() {
    vector<int> partition(n);
    vector<int> more_than_one(0);
    vector<int> coalition_size(k, 0);
    for (int i = 0; i < n; ++i) {
        partition[i] = rand() % k;
        coalition_size[partition[i]]++;
        if (coalition_size[partition[i]] == 2) more_than_one.push_back(partition[i]);
    }
    int ind = rand() % k;
    for (int i = 0; i < k; ++i) {
        ind += 1;
        ind %= k;
        if (coalition_size[ind] == 0)
            move_to_empty(partition, more_than_one, ind, coalition_size);
    }

    sum_edges.resize(k);
    for (int i = 0; i < k; ++i) {
        sum_edges[i].resize(n, 0);
    }
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            int Si = partition[i], Sj = partition[j];
            sum_edges[Si][j] += dist[i][j];
            sum_edges[Sj][i] += dist[i][j];
        }
    }
    return partition;
}

vector<int> Generate_zero_partition() {
    vector<int> partition(n, 0);
    vector<int> coalition_size(k, 0);

    sum_edges.resize(k);
    for (int i = 0; i < k; ++i) {
        sum_edges[i].resize(n, 0);
    }
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            sum_edges[0][i] += dist[i][j];
        }
    }
    return partition;
}

int GenerateLambda() {
    return 3 + rand() % (n / 3 + 3);
}

int count_dist(int p1, int p2) {
    return abs(p1 - p2);
}

void Update_sum_edges(Move move) {
    int v = move.v, Scv = move.Scv, Stv = move.Stv;
    for (int u = 0; u < n; ++u) {
        sum_edges[Scv][u] -= dist[u][v];
        sum_edges[Stv][u] += dist[u][v];
    }
}

int main() {
    std::fstream fin("../input.txt");
    std::ofstream fout("../output.txt");
    fin >> n >> k >> seconds;
    double p = 0.5;
    int w = 500, ksi = 1000, gamma_ = n / 10, lambda_;  // w = 500
    /*vector<int> params(n);
    for (int i = 0; i < n; ++i) {
        cin >> params[i];
    }
    int max_dist = 0;
    dist.resize(n);
    for (int i = 0; i < n; ++i) {
        dist[i].resize(n);
        for (int j = 0; j < n; ++j) {
            dist[i][j] = count_dist(params[i], params[j]);
            if (dist[i][j] > max_dist) max_dist = dist[i][j];
        }
    }*/

    dist.resize(n);
    for (int i = 0; i < n; ++i) {
        dist[i].resize(n);
        for (int j = 0; j < n; ++j) {
            fin >> dist[i][j];
            //cin >> dist[i][j];
        }
    }  // input dist


    //I = Generate_zero_partition();  // I is a partition, f(I) returns a number
    I = Generate_initial_partition();
    double f_I = f(I);
    double f_best = f_I, f_loc, f2, f1;
    vector<int> I_best(n);
    for (int i = 0; i < n; ++i) {
        I_best[i] = I[i];
    }  // I_best = I
    int cnon_impv = 0;
    Move move, move1, move2;


    gg = clock();
    bool globalimpr = true;
    int no_improvements = 0;
    while (clock() - gg < CLOCKS_PER_SEC * seconds) {
        //++cnt;
        // 1 & 2
        if (!globalimpr) ++no_improvements;
        else no_improvements = 0;
        globalimpr = false;
        bool improvement = true;
        while (improvement) {
            improvement = false;
            while (true) {
                if (clock() - gg > CLOCKS_PER_SEC * seconds) break;

                move = O1(I);
                f1 = Update_weight(f_I, move);
                if (f1 - f_I > eps) {
                    I = Update_partition(I, move);
                    f_I = f1;
                    Update_sum_edges(move);
                    improvement = true;
                    globalimpr = true;
                } else break;
            }
            if (clock() - gg > CLOCKS_PER_SEC * seconds) break;
            auto x = O2(I);
            move1 = x.first;
            move2 = x.second;
            f2 = f_I + dt(move1.v, move2.v, move1.Scv, move1.Stv, move2.Scv, move2.Stv);
            if (f2 - f_I > eps) {

                I = Update_partition(I, move1);
                Update_sum_edges(move1);
                I = Update_partition(I, move2);
                Update_sum_edges(move2);
                f_I = f2;
                improvement = true;
                globalimpr = true;
            }

        }
        f_loc = f_I;
        if (f_loc > f_best) {
            f_best = f_loc;
            I_best = I;
            cnon_impv = 0;
            globalimpr = true;
        } else cnon_impv = cnon_impv + 1;

        // 3 & 4
        tabu_set.clear();
        tabu_list.clear();
        int cdiv = 0; // Counter cdiv records number of diversified moves
        while (cdiv < w && f_loc - f_I >= eps) {

            if (clock() - gg > CLOCKS_PER_SEC * seconds) break;
            lambda_ = GenerateLambda();
            double r = (rand() % 100) / (100 * 1.0);
            if (r < p) {
                move = O3(I, lambda_);
                I = Update_partition(I, O3(I, lambda_));
                f_I = Update_weight(f_I, O3(I, lambda_));
                Update_tabu(lambda_, move); // Update_buckets tabu list H where λ is the tabu tenure
                Update_sum_edges(move);
            } else {

                auto x = O4(I);
                move1 = x.first;
                move2 = x.second;
                f2 = f_I + dt(move1.v, move2.v, move1.Scv, move1.Stv, move2.Scv, move2.Stv);
                I = Update_partition(I, move1);
                Update_sum_edges(move1);
                I = Update_partition(I, move2);
                Update_sum_edges(move2);
                f_I = f2;
                Update_tabu(lambda_, move1);
                Update_tabu(lambda_, move2);
            }
            cdiv++;
        }
        // 5
        if (cnon_impv > ksi) {
            for (int i = 0; i < gamma_; ++i) {   // Apply random perturbation γ times
                I = Update_partition(I, O5(I));
                f_I = Update_weight(f_I, O5(I));
                if (f_I > f_best) {  // ??
                    f_best = f_I;
                    I_best = I;
                    globalimpr = true;
                }
            }
            cnon_impv = 0;
        }
    }
    cout << f_best << "\n";
    for (int i : I_best) {
        cout << i << " ";
    }


    for (int v = 0; v < n; ++v) {
        fout << I_best[v] << " ";
    }
    return 0;
}