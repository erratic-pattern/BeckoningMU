"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia.objects.objects import DefaultExit, ExitCommand as DefaultExitCommand, SIGNAL_EXIT_TRAVERSED

from .objects import ObjectParent


class ExitCommand(DefaultExitCommand):
    """
    Default Exit command, used by the base exit object.

    This is a command that simply cause the caller to traverse
    the object it is attached to.

    """

    def func(self):
        """
        Default exit traverse if no syscommand is defined.
        """

        # Same logic as default Evennia ExitCommand, except we pass in the
        # session info so that we can use client width information
        if self.obj.access(self.caller, "traverse"):
            # we may traverse the exit.
            self.obj.at_traverse(self.caller, self.obj.destination, session=self.session)
            SIGNAL_EXIT_TRAVERSED.send(sender=self.obj, traverser=self.caller, session=self.session)
        else:
            # exit is locked
            if self.obj.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.obj.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.obj.at_failed_traverse(self.caller)


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_post_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    exit_command = ExitCommand

    def get_display_name(self, looker=None, **kwargs):
        # helper to create a clickable link
        def make_link(cmd, text):
            return f"|lc{cmd}|lt{text}|le"

        # create clickable link from name
        name_link = make_link(self.name, self.name)
        aliases = self.aliases.all()
        # list the first alias next to the full name of the exit.
        if aliases:
            alias = min(aliases, key=len)
            alias_link = make_link(alias, alias.upper())
            return f"<|w{alias_link}|n>  {name_link}"
        else:
            return name_link


    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This implements the actual traversal. The traverse lock has
        already been checked (in the Exit command) at this point.

        Args:
            traversing_object (DefaultObject): Object traversing us.
            target_location (DefaultObject): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        source_location = traversing_object.location
        if traversing_object.move_to(target_location, move_type="traverse", exit_obj=self, **kwargs):
            self.at_post_traverse(traversing_object, source_location, **kwargs)
        else:
            if self.db.err_traverse:
                # if exit has a better error message, let's use it.
                traversing_object.msg(self.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.at_failed_traverse(traversing_object, **kwargs)
