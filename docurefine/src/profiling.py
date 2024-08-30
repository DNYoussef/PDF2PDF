import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats()
        return result
    return wrapper