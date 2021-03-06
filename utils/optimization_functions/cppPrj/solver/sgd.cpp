#include "sgd.h"
#include <map>
template <typename T>
SGD<T>::SGD(const map<string, float> &config):BaseOptimizer<T>(config){
    // Ugly detail about templated classes (https://isocpp.org/wiki/faq/templates#nondependent-name-lookup-members)

    // Try to find key "learning_rate" returns an iterator if found
    auto search = BaseOptimizer<T>::m_config.find("learning_rate");

    // If we find "learning_rate" dereference the iterator to get associated value
    if (search != BaseOptimizer<T>::m_config.end()){
        m_base_lr = search->second;
    }
    else{
        throw("No learning rate set");
    }

}

template<typename T>
Tensor<T> SGD<T>::Optimize(const Tensor<T> &params, const Tensor<T> &grad_params, const OptimizerState<T> &state){

    // Gradient descent approach (Simpliest optimizer, no use of states)
    auto weights = params - (grad_params*m_base_lr);

    return weights;
}

/*
 * Explicit declare template versions to avoid linker error. (This is needed if we use templates on .cpp files)
*/
template class SGD<float>;
template class SGD<double>;
template class SGD<int>;

